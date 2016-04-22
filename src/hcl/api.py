import json
import os
import re
import sys

from .parser import HclParser


if sys.version_info[0] < 3:
    def u(s):
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, 'utf-8')
else:
    def u(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return s
    

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


def interpolate(data, variables):

    variable_reo = re.compile(r'^\$\{var\.(\w+)\}$')
    for key, value in data.iteritems():
        if isinstance(value, dict):
            interpolate(value, variables)
        else:
            if isinstance(value, basestring):
                match = variable_reo.match(value)
                if match is not None:
                    variable_name = match.groups(1)[0]
                    try:
                        default = variables[variable_name].get('default', '')
                    except KeyError:
                        default = None
                    data[key] = os.environ.get('TF_{}'.format(variable_name), default)


def interpolate_variables(base_path, data):
    variables_path = os.path.join(base_path, 'variables.tf')
    if os.path.exists(variables_path):
        with open(variables_path, 'r') as variables_fp:
            variables = HclParser().parse(variables_fp.read())['variable']
    else:
        variables = {}
    interpolate(data, variables)
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
