import sys

if sys.version_info[0] < 3:
    def iteritems(d):
        return iter(d.iteritems())

    def u(s):
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, 'utf-8')

    string_type = basestring
else:
    def iteritems(d):
        return iter(d.items())

    def u(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return s

    string_type = str
