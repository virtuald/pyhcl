import re
import sys

from .ply import lex

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
    raise ValueError(
        "Line %d, column %d, index %d: %s" % (lineno, column, lexpos, message)
    )


def _find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    column = (token.lexpos - last_cr) - 1
    return column


class Lexer(object):

    tokens = (
        'BOOL',
        'FLOAT',
        'NUMBER',
        'COMMA',
        'COMMENT',
        'MULTICOMMENT',
        'IDENTIFIER',
        'EQUAL',
        'STRING',
        'ADD',
        'MINUS',
        'MULTIPLY',
        'DIVIDE',
        'LEFTBRACE',
        'RIGHTBRACE',
        'LEFTBRACKET',
        'RIGHTBRACKET',
        'PERIOD',
        'EPLUS',
        'EMINUS',
        'LEFTPAREN',
        'RIGHTPAREN',
        'QMARK',
        'COLON',
        'ASTERISK_PERIOD',
        'GT',
        'LT',
        'EQ',
        'NE',
        'LE',
        'GE',
    )

    states = (
        ('stringdollar', 'exclusive'),
        ('string', 'exclusive'),
        ('heredoc', 'exclusive'),
        ('tabbedheredoc', 'exclusive'),
    )

    can_export_comments = []

    def t_BOOL(self, t):
        r'(true)|(false)'
        t.value = t.value == 'true'
        return t

    def t_EMINUS(self, t):
        r'(?<=\d|\.)[eE]-'
        return t

    def t_EPLUS(self, t):
        r'(?<=\d)[eE]\+?|(?<=\d\.)[eE]\+?'
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

    def t_COMMA(self, t):
        r','
        return t

    def t_QMARK(self, t):
        r'\?'
        return t

    def t_COLON(self, t):
        r':'
        return t

    def t_ASTERISK_PERIOD(self, t):
        r'\*\.'
        return t

    def t_GT(self, t):
        r'(?<!>)>(?!>|=)'
        return t

    def t_LT(self, t):
        r'(?<!<)<(?!<|=)'
        return t

    def t_EQ(self, t):
        r'=='
        return t

    def t_NE(self, t):
        r'!='
        return t

    def t_LE(self, t):
        r'<='
        return t

    def t_GE(self, t):
        r'>='
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
        t.lexer.string_value += (
            t.lexer.lexdata[t.lexer.rel_pos : t.lexer.lexpos - 2] + t.value
        )
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
        t.value = (
            t.lexer.string_value + t.lexer.lexdata[t.lexer.rel_pos : t.lexer.lexpos - 1]
        )
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start : t.lexer.lexpos - 1].count(
            '\n'
        )
        t.lexer.begin('INITIAL')
        return t

    def t_string_eof(self, t):
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start : t.lexer.lexpos].count(
            '\n'
        )
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
        t.lexer.lineno += t.lexer.lexdata[t.lexer.abs_start : t.lexer.lexpos].count(
            '\n'
        )
        _raise_error(t, "EOF before closing '${}' expression")

    def _init_heredoc(self, t):
        t.lexer.here_start = t.lexer.lexpos

        if t.value.endswith('\r\n'):
            t.lexer.newline_chars = 2
        else:
            t.lexer.newline_chars = 1

        if t.lexer.is_tabbed:
            # Chop '<<-'
            chop = 3
        else:
            # Chop '<<'
            chop = 2

        t.lexer.here_identifier = t.value[chop : -t.lexer.newline_chars]
        # We consumed a newline in the regex so bump the counter
        t.lexer.lineno += 1

    def t_tabbedheredoc(self, t):
        r'<<-\S+\r?\n'
        t.lexer.is_tabbed = True
        self._init_heredoc(t)
        t.lexer.begin('tabbedheredoc')

    def t_heredoc(self, t):
        r'<<\S+\r?\n'
        t.lexer.is_tabbed = False
        self._init_heredoc(t)
        t.lexer.begin('heredoc')

    def _end_heredoc(self, t):
        if t.lexer.is_tabbed:
            # Strip leading tabs
            value = t.value.strip()
        else:
            value = t.value

        if value == t.lexer.here_identifier:
            # Handle case where identifier is on a line of its own. Need to
            # subtract the current line and the newline characters from
            # the previous line to get the endpos
            endpos = t.lexer.lexpos - (t.lexer.newline_chars + len(t.value))
        elif value.endswith(t.lexer.here_identifier):
            # Handle case where identifier is at the end of the line. Need to
            # subtract the identifier from to get the endpos
            endpos = t.lexer.lexpos - len(t.lexer.here_identifier)
        else:
            return

        entire_string = t.lexer.lexdata[t.lexer.here_start : endpos]

        if t.lexer.is_tabbed:
            # Get rid of any initial tabs, and remove any tabs preceded by
            # a new line
            chopped_starting_tabs = re.sub('^\t*', '', entire_string)
            t.value = re.sub('\n\t*', '\n', chopped_starting_tabs)
        else:
            t.value = entire_string

        t.lexer.lineno += t.lexer.lexdata[t.lexer.here_start : t.lexer.lexpos].count(
            '\n'
        )
        t.lexer.begin('INITIAL')
        return t

    def t_tabbedheredoc_STRING(self, t):
        r'^\t*.+?(?=\r?$)'
        return self._end_heredoc(t)

    def t_heredoc_STRING(self, t):
        r'^.+?(?=\r?$)'
        return self._end_heredoc(t)

    def t_heredoc_ignoring(self, t):
        r'.+|\n'
        pass

    def t_heredoc_eof(self, t):
        t.lexer.lineno += t.lexer.lexdata[t.lexer.here_start : t.lexer.lexpos].count(
            '\n'
        )
        _raise_error(t, 'EOF before closing heredoc')

    t_tabbedheredoc_ignoring = t_heredoc_ignoring
    t_tabbedheredoc_eof = t_heredoc_eof

    t_LEFTBRACE = r'\{'
    t_RIGHTBRACE = r'\}'
    t_LEFTBRACKET = r'\['
    t_RIGHTBRACKET = r'\]'
    t_LEFTPAREN = r'\('
    t_RIGHTPAREN = r'\)'

    def t_COMMENT(self, t):
        r'(\#|(//)).*'
        if 'COMMENT' in self.can_export_comments:
            t.value = t.value.lstrip('#').lstrip('//').lstrip()
            return t

    def t_MULTICOMMENT(self, t):
        r'/\*(.|\n)*?(\*/)'
        t.lexer.lineno += t.value.count('\n')
        if 'MULTICOMMENT' in self.can_export_comments:
            return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t\r\f\v'

    t_EQUAL = r'(?<!=)=(?!=)'
    t_ADD = r'\+'
    t_MINUS = r'-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'

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

    def __init__(self, export_comments=None):
        if export_comments is not None:
            if export_comments == 'LINE':
                self.can_export_comments = ['COMMENT']
            elif export_comments == 'MULTILINE':
                self.can_export_comments = ['MULTICOMMENT']
            elif export_comments == 'ALL':
                self.can_export_comments = ['COMMENT', 'MULTICOMMENT']
            else:
                raise ValueError(
                    'Only `LINE`, `MULTILINE` and `ALL` value are allowed for '
                    '`export_comments`. given: `%s`.' % export_comments
                )

        self.lex = lex.lex(
            module=self,
            debug=False,
            reflags=(re.UNICODE | re.MULTILINE),
            errorlog=lex.NullLogger(),
        )

    def input(self, s):
        return self.lex.input(s)

    def token(self):
        return self.lex.token()
