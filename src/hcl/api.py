import json
from .parser import HclParser

import sys

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


def load(fp, object_pairs_hook=None):
    '''
        Deserializes a file-pointer like object into a python dictionary.
        The contents of the file must either be JSON or HCL.
        
        :param fp: An object that has a read() function
        :param object_pairs_hook: is an optional function that behaves just like the json.load parameter does but only supports OrderedDict
        :returns: Dictionary
    '''
    return loads(fp.read(), object_pairs_hook=object_pairs_hook)


def loads(s, object_pairs_hook=None):
    '''
        Deserializes a string and converts it to a dictionary. The contents
        of the string must either be JSON or HCL.

        :param object_pairs_hook: is an optional function that behaves just like the json.load parameter does but only supports OrderedDict

        :returns: Dictionary 
    '''
    s = u(s)
    if isHcl(s):
        hcl_out = HclParser(object_pairs_hook=object_pairs_hook)
        return hcl_out.parse(s)
    else:
        return json.loads(s, object_pairs_hook=object_pairs_hook)


def dumps(*args, **kwargs):
    '''Turns a dictionary into JSON, passthru to json.dumps'''
    return json.dumps(*args, **kwargs)
