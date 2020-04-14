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
    if not s:
        return True

    for c in s:
        if c.isspace():
            continue

        if c == '{':
            return False
        else:
            return True

    raise ValueError("No HCL object could be decoded")


def load(fp, export_comments=None):
    '''
        Deserializes a file-pointer like object into a python dictionary.
        The contents of the file must either be JSON or HCL.
        
        :param fp: An object that has a read() function
        :param export_comments: optional string that allow to export also coded comments. it could be:
            'LINE': to export only single-line comments (// or #)
            'MULTILINE': to export only multi-line comments (/* ... */)
            'ALL': to export both 'LINE' and 'MULTILINE' comments
            default None
        
        :returns: Dictionary
    '''
    return loads(fp.read(), export_comments=export_comments)


def loads(s, export_comments=None):
    '''
        Deserializes a string and converts it to a dictionary. The contents
        of the string must either be JSON or HCL.
        
        :param s: string to parse
        :param export_comments: optional string that allow to export also coded comments. it could be:
            'LINE': to export only single-line comments (// or #)
            'MULTILINE': to export only multi-line comments (/* ... */)
            'ALL': to export both 'LINE' and 'MULTILINE' comments
            default None
        
        :returns: Dictionary 
    '''
    s = u(s)
    if isHcl(s):
        return HclParser().parse(s, export_comments=export_comments)
    else:
        return json.loads(s)


def dumps(*args, **kwargs):
    '''Turns a dictionary into JSON, passthru to json.dumps'''
    return json.dumps(*args, **kwargs)
