import re
import sys
import ply.lex as lex

if sys.version_info < (3,):
    text_type = unicode
else:
    text_type = str

def _raise_error(t, message=None):
    lexpos = t.lexer.lexpos
    lexdata = t.lexer.lexdata
    lineno = t.lexer.lineno
    column = _find_column(lexdata, t)
    if message is None:
        message = "Illegal character '%s'" % lexdata[lexpos]
    raise ValueError("Line %d, column %d, index %d: %s" % (lineno, column, lexpos, message))

def _find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    column = (token.lexpos - last_cr) - 1
    return column

class Lexer(object):

    tokens = (
        'BOOL',
        'FLOAT',
        'NUMBER',
        'COMMA', 'COMMAEND', 'IDENTIFIER', 'EQUAL', 'STRING', 'MINUS',
        'LEFTBRACE', 'RIGHTBRACE', 'LEFTBRACKET', 'RIGHTBRACKET', 'PERIOD',
        'EPLUS', 'EMINUS',
    )

    states = (
        ('stringdollar', 'exclusive'),
        ('string', 'exclusive'),
        ('heredoc', 'exclusive'),
    )

    def t_BOOL(self, t):
        r'(true)|(false)'
        return t

    def t_EMINUS(self, t):
        r'(?<=\d|\.)[eE]-'
        return t

    def t_EPLUS(self, t):
        r'(?<=\d|\.)[eE]\+?'
        return t

    def t_FLOAT(self, t):
        r'-?((\d+\.\d*)|(\d*\.\d+))'
        t.value = float(t.value)
        return t

    def t_hexnumber(self, t):
        r'-?0[xX][0-9a-fA-F]+'
        t.value = int(t.value, base=16)
        t.type = 'NUMBER'
        return t

    def t_intnumber(self, t):
        r'-?\d+'
        t.value = int(t.value)
        t.type = 'NUMBER'
        return t

    def t_PERIOD(self, t):
        r'\.'
        return t

    def t_COMMAEND(self, t):
        r',(?=\s*\])'
        return t

    def t_COMMA(self, t):
        r','
        return t

    def t_IDENTIFIER(self, t):
        r'[^\W\d][\w.-]*'
        t.value = text_type(t.value)
        return t

    # Strings
    def t_string(self, t):
        # Start of a string
        r'\"'
        # abs_start is the absolute start of the string. We use this at the end
        # to know how many new lines we've consumed
        t.lexer.abs_start = t.lexer.lexpos
        # rel_pos is the begining of the unconsumed part of the string. It will
        # get modified when consuming escaped characters
        t.lexer.rel_pos = t.lexer.lexpos
        # The value of the consumed part of the string
        t.lexer.string_value = u''
        t.lexer.begin('string')

    def t_string_escapedchar(self, t):
        # If a quote or backslash is escaped, build up the string by ignoring
        # the escape character. Should this be done for other characters?
        r'(?<=\\)(\"|\\)'
        t.lexer.string_value += t.lexer.lexdata[t.lexer.rel_pos:t.lexer.lexpos - 2] + t.value
        t.lexer.rel_pos = t.lexer.lexpos
        pass

    def t_string_stringdollar(self, t):
        # Left brace preceeded by a dollar
        r'(?<=\$)\{'
        t.lexer.braces = 1
        t.lexer.begin('stringdollar')

    def t_string_ignoring(self, t):
        # Ignore everything except for a quote
        r'[^\"]'
        pass

    def t_string_STRING(self, t):
        # End of the string
        r'\"'
        t.value = t.lexer.string_value + t.lexer.lexdata[t.lexer.rel_pos:t.lexer.lexpos - 1]
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start:t.lexer.lexpos - 1].count('\n')
        t.lexer.begin('INITIAL')
        return t

    def t_string_eof(self, t):
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start:t.lexer.lexpos].count('\n')
        _raise_error(t, 'EOF before closing string quote')

    def t_stringdollar_dontcare(self, t):
        # Ignore everything except for braces
        r'[^\{\}]'
        pass

    def t_stringdollar_lbrace(self, t):
        r'\{'
        t.lexer.braces += 1

    def t_stringdollar_rbrace(self, t):
        r'\}'
        t.lexer.braces -= 1

        if t.lexer.braces == 0:
            # End of the dollar brace, back to the rest of the string
            t.lexer.begin('string')

    def t_stringdollar_eof(self, t):
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start:t.lexer.lexpos].count('\n')
        _raise_error(t, "EOF before closing '${}' expression")

    def t_heredoc(self, t):
        r'<<\S+(?=\n)'
        t.lexer.here_start = t.lexer.lexpos
        t.lexer.here_identifier = t.value[2:]
        t.lexer.begin('heredoc')

    def t_heredoc_STRING(self, t):
        r'^\S+$'
        if t.value == t.lexer.here_identifier:
            # Need to subtract the identifier and \n from the lexpos to get the
            # endpos
            endpos = t.lexer.lexpos - (1 + len(t.lexer.here_identifier))
            # The startpos is one character after the here_start to account for
            # the newline
            t.value = t.lexer.lexdata[t.lexer.here_start + 1:endpos]
            t.lexer.lineno += t.lexer.lexdata[t.lexer.here_start:t.lexer.lexpos].count('\n')
            t.lexer.begin('INITIAL')
            return t

    def t_heredoc_ignoring(self, t):
        r'.+|\n'
        pass

    def t_heredoc_eof(self, t):
        t.lexer.lineno += t.lexer.lexdata[t.lexer.here_start:t.lexer.lexpos].count('\n')
        _raise_error(t, 'EOF before closing heredoc')

    t_EQUAL = r'='
    t_MINUS = r'-'

    t_LEFTBRACE = r'\{'
    t_RIGHTBRACE = r'\}'
    t_LEFTBRACKET = r'\['
    t_RIGHTBRACKET = r'\]'

    def t_COMMENT(self, t):
        r'(\#|(//)).*'
        pass

    def t_MULTICOMMENT(self, t):
        r'/\*(.|\n)*?(\*/)'
        t.lexer.lineno += t.value.count('\n')
        pass

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t\r\f\v'

    # Error handling rule
    def t_error(self, t):
        if t.value.startswith('/*'):
            _raise_error(t, 'EOF before closing multiline comment')
        elif t.value.startswith('*/'):
            _raise_error(t, "Found '*/' before start of multiline comment")
        elif t.value.startswith('/'):
            c = t.value[1]
            _raise_error(t, "Expected '//' for comment, got '/%s'" % c)
        elif t.value.startswith('<<'):
            _raise_error(t, "Heredoc must have a marker, e.g. '<<FOO'")
        elif t.value.startswith('<'):
            c = t.value[1]
            _raise_error(t, "Heredoc must start with '<<', got '<%s'" % c)
        else:
            _raise_error(t)

    def __init__(self):
        self.lex = lex.lex(module=self, debug=False, reflags=(re.UNICODE | re.MULTILINE))

    def input(self, s):
        return self.lex.input(s)

    def token(self):
        return self.lex.token()
