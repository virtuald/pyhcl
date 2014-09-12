
import json
from .parser import HclParser

import sys


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


def load(fp):
    '''
        Deserializes a file-pointer like object into a python dictionary.
        The contents of the file must either be JSON or HCL.
        
        :param fp: An object that has a read() function
    '''
    return loads(fp.read())

def loads(s):
    '''
        Deserializes a string and converts it to a dictionary. The contents
        of the string must either be JSON or HCL.
        
        :returns: Dictionary 
    '''
    s = s.decode('utf-8')
    if isHcl(s):
        return HclParser().parse(s)
    else:
        return json.loads(s)
    

def dumps(*args, **kwargs):
    '''Turns a dictionary into JSON, passthru to json.dumps'''
    return json.dumps(*args, **kwargs)

