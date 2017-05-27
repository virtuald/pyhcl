import json
import os
import re

from .compat import iteritems, string_type, u
from .parser import HclParser


def isHcl(s):
    '''
        Detects whether a string is JSON or HCL
        
        :param s: String that may contain HCL or JSON
        
        :returns: True if HCL, False if JSON, raises ValueError
                  if neither
    '''
    for c in s:
        if c.isspace():
            continue
        
        if c == '{':
            return False
        else:
            return True
        
    raise ValueError("No HCL object could be decoded")


def interpolate(value, variables):
    variable_reo = re.compile(r'^\$\{var\.(\w+)\}$')
    match = variable_reo.match(value)
    if match is not None:
        variable_name = match.groups(1)[0]
        try:
            default = variables[variable_name].get('default', '')
        except KeyError:
            default = ''
        return os.environ.get('TF_VAR_{}'.format(variable_name), default)
    return value


def interpolate_list(data, variables):
    values = []
    for value in data:
        if isinstance(value, dict):
            interpolate_func = interpolate_dict
        elif isinstance(value, list):
            interpolate_func = interpolate_list
        elif isinstance(value, string_type):
            interpolate_func = interpolate
        values.append(interpolate_func(value, variables))
    return values


def interpolate_dict(data, variables):
    for key, value in iteritems(data):
        if isinstance(value, dict):
            interpolate_dict(value, variables)
        elif isinstance(value, list):
            data[key] = interpolate_list(value, variables)
        elif isinstance(value, string_type):
            data[key] = interpolate(value, variables)
    return data


def interpolate_variables(base_path, data):
    variables_path = os.path.join(base_path, 'variables.tf')
    if os.path.exists(variables_path):
        with open(variables_path, 'r') as variables_fp:
            variables = HclParser().parse(variables_fp.read())['variable']
    else:
        variables = {}
    interpolate_dict(data, variables)
    return data


def load(fp):
    '''
        Deserializes a file-pointer like object into a python dictionary.
        The contents of the file must either be JSON or HCL.
        
        :param fp: An object that has a read() function
        
        :returns: Dictionary
    '''
    data = loads(fp.read())
    fp_path = os.path.split(fp.name)[0]
    return interpolate_variables(fp_path, data)

def loads(s):
    '''
        Deserializes a string and converts it to a dictionary. The contents
        of the string must either be JSON or HCL.
        
        :returns: Dictionary 
    '''
    s = u(s)
    if isHcl(s):
        return HclParser().parse(s)
    else:
        return json.loads(s)

def dumps(*args, **kwargs):
    '''Turns a dictionary into JSON, passthru to json.dumps'''
    return json.dumps(*args, **kwargs)
