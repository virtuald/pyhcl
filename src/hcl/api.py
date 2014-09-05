
import json
from .parser import HclParser

import sys


def isHcl(s):
    for c in s:
        if c.isspace():
            continue
        
        if c == '{':
            return False
        else:
            return True
        
    raise ValueError("No HCL object could be decoded")


def load(fp):
    return loads(fp.read())

def loads(s):
    '''
        Creates a dictionary out of an HCL-formatted string or a JSON string
        
        TODO: Multiple threads
    '''
    if isHcl(s):
        if sys.version_info[0] < 3 and isinstance(s, unicode):
            s = unicode(s, 'utf-8')
        return HclParser().parse(s)
    else:
        return json.loads(s)
    

def dumps(*args, **kwargs):
    '''Turns a dictionary into JSON, passthru to json.dumps'''
    return json.dumps(*args, **kwargs)

