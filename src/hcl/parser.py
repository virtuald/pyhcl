from os.path import abspath, dirname, exists, join
import sys

from .lexer import Lexer
from .ply import yacc

import inspect

DEBUG = False

# When using something like pyinstaller, the __file__ attribute isn't actually
# set correctly, so the parse file isn't able to be saved anywhere sensible.
# In these cases, just use a temporary directory, it doesn't take too long to
# generate the tables anyways...

if exists(dirname(__file__)):
    pickle_file = abspath(join(dirname(__file__), 'parsetab.dat'))
else:
    import tempfile

    fobj = tempfile.NamedTemporaryFile()
    pickle_file = fobj.name


if sys.version_info[0] < 3:

    def iteritems(d):
        return iter(d.iteritems())

    string_types = (str, unicode)


else:

    def iteritems(d):
        return iter(d.items())

    string_types = (str, bytes)


class HclParser(object):

    #
    # Tokens
    #

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

    #
    # Yacc parser section
    #
    def objectlist_flat(self, lt, replace):
        '''
            Similar to the dict constructor, but handles dups

            HCL is unclear on what one should do when duplicate keys are
            encountered. These comments aren't clear either:

            from decoder.go: if we're at the root or we're directly within
                             a list, decode into dicts, otherwise lists

            from object.go: there's a flattened list structure
        '''
        d = {}

        for k, v in lt:
            if k in d.keys() and not replace:
                if type(d[k]) is list:
                    d[k].append(v)
                else:
                    d[k] = [d[k], v]
            else:
                if isinstance(v, dict):
                    dd = d.setdefault(k, {})
                    for kk, vv in iteritems(v):
                        if type(dd) == list:
                            dd.append({kk: vv})
                        elif kk in dd.keys():
                            if hasattr(vv, 'items'):
                                for k2, v2 in iteritems(vv):
                                    dd[kk][k2] = v2
                            else:
                                d[k] = [dd, {kk: vv}]
                        else:
                            dd[kk] = vv
                else:
                    d[k] = v

        return d

    def p_top(self, p):
        '''
        top : empty
            | objectlist
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[1], True)

    def p_empty_0(self, p):
        '''
        empty :
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = []

    def p_objectlist_0(self, p):
        "objectlist : objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1]]

    def p_objectlist_1(self, p):
        "objectlist : objectlist objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[2]]

    def p_objectlist_2(self, p):
        "objectlist : objectlist COMMA objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[3]]

    def p_object_0(self, p):
        "object : LEFTBRACE objectlist RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[2], False)

    def p_object_1(self, p):
        "object : LEFTBRACE objectlist COMMA RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[2], False)

    def p_object_2(self, p):
        "object : LEFTBRACE RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = {}

    def p_objectkey_0(self, p):
        '''
        objectkey : IDENTIFIER
                  | STRING
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_objectkey_1(self, p):
        '''
        objectkey : IDENTIFIER ADD number
                  | number ADD IDENTIFIER
                  | IDENTIFIER MINUS number
                  | number MINUS IDENTIFIER
                  | IDENTIFIER MULTIPLY number
                  | number MULTIPLY IDENTIFIER
                  | IDENTIFIER DIVIDE number
                  | number DIVIDE IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = (str(p[1]), str(p[2]), str(p[3]))

    def p_objectbrackets_0(self, p):
        "objectbrackets : IDENTIFIER LEFTBRACKET objectkey RIGHTBRACKET"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + p[3] + p[4]

    def p_objectbrackets_1(self, p):
        '''
        objectbrackets : IDENTIFIER LEFTBRACKET objectkey RIGHTBRACKET PERIOD IDENTIFIER
                       | IDENTIFIER LEFTBRACKET NUMBER RIGHTBRACKET PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + str(p[3]) + p[4] + p[5] + p[6]

    def p_objectitem_0(self, p):
        '''
        objectitem : objectkey EQUAL number
                   | objectkey EQUAL BOOL
                   | objectkey EQUAL STRING
                   | objectkey EQUAL IDENTIFIER
                   | objectkey EQUAL object
                   | objectkey EQUAL objectkey
                   | objectkey EQUAL list
                   | objectkey EQUAL objectbrackets
                   | objectkey EQUAL function
                   | objectkey EQUAL booleanexp
                   | objectkey COLON number
                   | objectkey COLON BOOL
                   | objectkey COLON STRING
                   | objectkey COLON IDENTIFIER
                   | objectkey COLON object
                   | objectkey COLON objectkey
                   | objectkey COLON list
                   | objectkey COLON objectbrackets
                   | objectkey COLON booleanexp
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], p[3])

    def p_objectitem_1(self, p):
        "objectitem : block"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_objectitem_2(self, p):
        '''
        objectitem : objectkey EQUAL objectkey QMARK objectkey COLON objectkey
                   | objectkey EQUAL objectkey QMARK objectkey COLON number
                   | objectkey EQUAL objectkey QMARK objectkey COLON BOOL
                   | objectkey EQUAL objectkey QMARK objectkey COLON function
                   | objectkey EQUAL objectkey QMARK number COLON objectkey
                   | objectkey EQUAL objectkey QMARK BOOL COLON objectkey
                   | objectkey EQUAL objectkey QMARK function COLON objectkey
                   | objectkey EQUAL objectkey QMARK number COLON number
                   | objectkey EQUAL objectkey QMARK number COLON BOOL
                   | objectkey EQUAL objectkey QMARK number COLON function
                   | objectkey EQUAL objectkey QMARK BOOL COLON number
                   | objectkey EQUAL objectkey QMARK BOOL COLON function
                   | objectkey EQUAL objectkey QMARK BOOL COLON BOOL
                   | objectkey EQUAL booleanexp QMARK objectkey COLON objectkey
                   | objectkey EQUAL booleanexp QMARK objectkey COLON number
                   | objectkey EQUAL booleanexp QMARK objectkey COLON BOOL
                   | objectkey EQUAL booleanexp QMARK objectkey COLON function
                   | objectkey EQUAL booleanexp QMARK number COLON objectkey
                   | objectkey EQUAL booleanexp QMARK BOOL COLON objectkey
                   | objectkey EQUAL booleanexp QMARK function COLON objectkey
                   | objectkey EQUAL booleanexp QMARK number COLON number
                   | objectkey EQUAL booleanexp QMARK number COLON BOOL
                   | objectkey EQUAL booleanexp QMARK number COLON function
                   | objectkey EQUAL booleanexp QMARK BOOL COLON number
                   | objectkey EQUAL booleanexp QMARK BOOL COLON function
                   | objectkey EQUAL booleanexp QMARK BOOL COLON BOOL
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], p[3] + p[4] + str(p[5]) + p[6] + str(p[7]))

    def p_operator_0(self, p):
        '''
        operator : EQ
                 | NE
                 | LT
                 | GT
                 | LE
                 | GE
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_booleanexp_0(self, p):
        '''
        booleanexp : objectkey operator objectkey
                   | objectkey operator number
                   | number operator objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = str(p[1]) + p[2] + str(p[3])

    def p_block_0(self, p):
        "block : objectkey object"
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], p[2])

    def p_block_1(self, p):
        "block : objectkey block"
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], {p[2][0]: p[2][1]})

    def p_list_0(self, p):
        '''
        list : LEFTBRACKET listitems RIGHTBRACKET
             | LEFTBRACKET listitems COMMA RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[2]

    def p_list_1(self, p):
        '''
        list : LEFTBRACKET RIGHTBRACKET
             | LEFTPAREN RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = []

    def p_list_2(self, p):
        '''
        list : LEFTPAREN LEFTBRACKET listitems RIGHTBRACKET PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[3]] + [p[5] + p[6] + p[7]]

    def p_list_of_lists_0(self, p):
        '''
        list_of_lists : list COMMA list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1], p[3]

    def p_list_of_lists_1(self, p):
        '''
        list_of_lists : list_of_lists COMMA list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + (p[3],)

    def p_function_0(self, p):
        '''
        function : IDENTIFIER LEFTPAREN listitems RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list_of_lists RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[4]

    def p_function_1(self, p):
        '''
        function : IDENTIFIER LEFTPAREN listitems COMMA RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list_of_lists COMMA RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[5]

    def p_function_2(self, p):
        '''
        function : IDENTIFIER LEFTPAREN list PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[4] + p[5] + p[6] + p[7]

    def p_function_3(self, p):
        '''
        function : IDENTIFIER LEFTPAREN LEFTBRACKET list_of_lists RIGHTBRACKET PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = (
            p[1] + p[2] + p[3] + self.flatten(p[4]) + p[5] + p[6] + p[7] + p[8] + p[9]
        )

    def flatten(self, value):
        if isinstance(value, dict):
            return (
                "{"
                + ",".join(key + ":" + self.flatten(value[key]) for key in value)
                + "}"
            )
        if isinstance(value, list):
            return ",".join(self.flatten(v) for v in value)
        if isinstance(value, tuple):
            return " ".join(self.flatten(v) for v in value)
        if isinstance(value, string_types):
            if sys.version_info[0] < 3:
                if value.isdigit():  # python2 support, return numbers as is
                    return value
            else:
                if value.isnumeric():  # return numbers as is
                    return value
            return (
                '"' + value + '"'  # wrap string literals in double quotes
                if value not in ['+', '-'] and '.' not in value
                else value  # but not if its var interpolation or an operator
            )
        raise TypeError(
            '%s is of type %s; expected type of dict, list, tuple, or str',
            str(value),
            type(value),
        )

    def p_listitems_0(self, p):
        '''
        listitems : listitem
                  | function
                  | object COMMA
                  | objectkey COMMA
                  | list COMMA
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1]]

    def p_listitems_1(self, p):
        '''
        listitems : listitems COMMA listitem
                  | listitems COMMA function
                  | listitems COMMA objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[3]]

    def p_listitems_2(self, p):
        '''
        listitems : object COMMA object
                  | object COMMA objectkey
                  | objectkey COMMA objectkey
                  | objectkey COMMA object
                  | objectkey COMMA list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1], p[3]]

    def p_listitems_3(self, p):
        '''
        listitems : objectkey COMMA IDENTIFIER ASTERISK_PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1], p[3] + p[4] + p[5]]

    def p_listitems_4(self, p):
        '''
        listitems : objectkey list
        '''
        if DEBUG:
            self.print_p(p)
        p[2].insert(0, p[1])
        p[0] = p[2]

    def p_listitems_5(self, p):
        '''
        listitems : listitems COMMA COMMENT
                  | listitems COMMA MULTICOMMENT
        '''
        # skip comments in lists
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_listitem_0(self, p):
        '''
        listitem : number
                 | object
                 | objectkey
                 | objectbrackets
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_listitem_1(self, p):
        '''
        listitem : IDENTIFIER ASTERISK_PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + p[3]

    def p_number_0(self, p):
        "number : int"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_number_1(self, p):
        "number : float"
        if DEBUG:
            self.print_p(p)
        p[0] = float(p[1])

    def p_number_2(self, p):
        "number : int exp"
        if DEBUG:
            self.print_p(p)
        p[0] = float("{0}{1}".format(p[1], p[2]))

    def p_number_3(self, p):
        "number : float exp"
        if DEBUG:
            self.print_p(p)
        p[0] = float("{0}{1}".format(p[1], p[2]))

    def p_number_4(self, p):
        '''
        number : number ADD number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[3]

    def p_number_5(self, p):
        '''
        number : number MINUS number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] - p[3]

    def p_number_6(self, p):
        '''
        number : number MULTIPLY number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] * p[3]

    def p_number_7(self, p):
        '''
        number : number DIVIDE number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] / p[3]

    def p_int_0(self, p):
        "int : MINUS int"
        if DEBUG:
            self.print_p(p)
        p[0] = -p[2]

    def p_int_1(self, p):
        "int : NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_float_0(self, p):
        "float : MINUS float"
        p[0] = p[2] * -1

    def p_float_1(self, p):
        "float : FLOAT"
        p[0] = p[1]

    def p_exp_0(self, p):
        "exp : EPLUS NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = "e{0}".format(p[2])

    def p_exp_1(self, p):
        "exp : EMINUS NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = "e-{0}".format(p[2])

    def p_comment_0(self, p):
        '''
        block : COMMENT
              | MULTICOMMENT
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = ("comment-L{:03d}".format(p.lineno(1)), p[1])

    # useful for debugging the parser
    def print_p(self, p):
        if DEBUG:
            name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
            print(
                '%20s: %s' % (name, ' | '.join([str(p[i]) for i in range(0, len(p))]))
            )

    def p_error(self, p):
        # Derived from https://groups.google.com/forum/#!topic/ply-hack/spqwuM1Q6gM

        # Ugly hack since Ply doesn't provide any useful error information
        try:
            frame = inspect.currentframe()
            cvars = frame.f_back.f_locals
            expected = "; expected %s" % (
                ', '.join(cvars['actions'][cvars['state']].keys())
            )
        except:
            expected = ""

        if p is not None:
            msg = "Line %d, column %d: unexpected %s%s" % (
                p.lineno,
                p.lexpos,
                p.type,
                expected,
            )
        else:
            msg = "Unexpected end of file%s" % expected

        raise ValueError(msg)

    def __init__(self):
        self.yacc = yacc.yacc(
            module=self, debug=False, optimize=1, debugfile=pickle_file
        )

    def parse(self, s, export_comments=None):
        return self.yacc.parse(
            s, lexer=Lexer(export_comments=export_comments), debug=DEBUG
        )
