# -*- coding: UTF-8 -*-
#
# These tests are taken from hcl/lex_test.go
#

from __future__ import print_function, unicode_literals

from os.path import join, dirname
import hcl.lexer

import pytest

class Error:
    pass

LEX_FIXTURE_DIR = join(dirname(__file__), 'lex-fixtures')
LEX_FIXTURES = [
    (
        "array_comment.hcl",
        ["IDENTIFIER", "EQUAL", "LEFTBRACKET",
        "STRING", "COMMA",
        "STRING", "COMMA",
        "RIGHTBRACKET", None]
    ),
    (
        "comment.hcl",
        ["IDENTIFIER", "EQUAL", "STRING", None]
    ),
    (
        "multiple.hcl",
        [
            "IDENTIFIER", "EQUAL", "STRING",
            "IDENTIFIER", "EQUAL", "NUMBER",
            None,
        ],
    ),
    (
        "list.hcl",
        [
            "IDENTIFIER", "EQUAL", "LEFTBRACKET",
            "NUMBER", "COMMA", "NUMBER", "COMMA", "STRING",
            "RIGHTBRACKET", None,
        ],
    ),
    (
        "list_comma.hcl",
        [
            "IDENTIFIER", "EQUAL", "LEFTBRACKET",
            "NUMBER", "COMMA", "NUMBER", "COMMA", "STRING",
            "COMMAEND", "RIGHTBRACKET", None,
        ],
    ),
    (
        "structure_basic.hcl",
        [
            "IDENTIFIER", "LEFTBRACE",
            "IDENTIFIER", "EQUAL", "NUMBER",
            "STRING", "EQUAL", "NUMBER",
            "STRING", "EQUAL", "NUMBER",
            "RIGHTBRACE", None,
        ],
    ),
    (
        "structure.hcl",
        [
            "IDENTIFIER", "IDENTIFIER", "STRING", "LEFTBRACE",
            "IDENTIFIER", "EQUAL", "NUMBER",
            "IDENTIFIER", "EQUAL", "STRING",
            "RIGHTBRACE", None,
        ],
    ),
]

# The first value in the tuple can be either the file that will be read or just
# a string
LEX_ERROR_FIXTURES = [
    (
        "old.hcl",
        [
            "IDENTIFIER", "EQUAL", "LEFTBRACE", "STRING", Error
        ],
        "Line 2, column 15, index 27: Illegal character ':'"
    ),
    (
        "unterminated_block_comment.hcl",
        [Error],
        "Line 1, column 0, index 0: EOF before closing multiline comment"
    ),
    (
        "nested_comment.hcl",
        [Error],
        "Line 5, column 0, index 13: Found '*/' before start of multiline comment"
    ),
    (
        "/not a comment",
        [Error],
        "Line 1, column 0, index 0: Expected '//' for comment, got '/n'"
    ),
    (
        "a = <HERE\n"
        "foobar\n"
        "HERE",
        ["IDENTIFIER", "EQUAL", Error],
        "Line 1, column 4, index 4: Heredoc must start with '<<', got '<H'"
    ),
    (
        "a = <<HE RE\n"
        "foobar\n"
        "HERE",
        ["IDENTIFIER", "EQUAL", Error],
        "Line 1, column 4, index 4: Heredoc must have a marker, e.g. '<<FOO'"
    ),
    (
        "a = <<HERE\n"
        "foobar\n",
        ["IDENTIFIER", "EQUAL", Error],
        "Line 3, column 0, index 18: EOF before closing heredoc"
    ),
    (
        'a = "foo',
        ["IDENTIFIER", "EQUAL", Error],
        "Line 1, column 8, index 8: EOF before closing string quote"
    ),
    (
        'a = "${foo"',
        ["IDENTIFIER", "EQUAL", Error],
        "Line 1, column 11, index 11: EOF before closing '${}' expression"
    ),

]

@pytest.mark.parametrize("hcl_fname,tokens", LEX_FIXTURES)
def test_lexer(hcl_fname, tokens):
    
    with open(join(LEX_FIXTURE_DIR, hcl_fname), 'r') as fp:
        input = fp.read()
    
    print(input)
    
    lexer = hcl.lexer.Lexer()
    lexer.input(input)

    for tok in tokens:
        lex_tok = lexer.token()
            
        if lex_tok is None:
            assert tok is None
        else:
            assert tok == lex_tok.type 
        print(lex_tok)
            
    assert lexer.token() is None

@pytest.mark.parametrize("hcl_fname,tokens,error_loc", LEX_ERROR_FIXTURES)
def test_lexer_errors(hcl_fname, tokens, error_loc):

    if hcl_fname.endswith('.hcl'):
        with open(join(LEX_FIXTURE_DIR, hcl_fname), 'r') as fp:
            input = fp.read()
    else:
        input = hcl_fname

    print(input)

    lexer = hcl.lexer.Lexer()
    lexer.input(input)

    for tok in tokens:
        try:
            lex_tok = lexer.token()
        except ValueError as e:
            assert tok is Error
            assert error_loc == str(e)
            return

        if lex_tok is None:
            assert tok is None
        else:
            assert tok == lex_tok.type
        print(lex_tok)

f100 = 'f' * 100

TOKEN_FIXTURES = [
    # Comments
    (None, "//"),
    (None, "////"),
    (None, "// comment"),
    (None, "// /* comment */"),
    (None, "// // comment //"),
    (None, "//" + f100),
    (None, "#"),
    (None, "##"),
    (None, "# comment"),
    (None, "# /* comment */"),
    (None, "# # comment #"),
    (None, "#" + f100),
    (None, "/**/"),
    (None, "/***/"),
    (None, "/* comment */"),
    (None, "/* // comment */"),
    (None, "/* /* comment */"),
    (None, "/*\n comment\n*/"),
    (None, "/*" + f100 + "*/"),

    # Operators
    ("LEFTBRACKET", "["),
    ("LEFTBRACE", "{"),
    ("COMMA", ","),
    ("PERIOD", "."),
    ("RIGHTBRACKET", "]"),
    ("RIGHTBRACE", "}"),
    ("EQUAL", "="),
    ("MINUS", "-"),

    # Bools
    ("BOOL", "true"),
    ("BOOL", "false"),

    # Identifier
    ("IDENTIFIER", "a"),
    ("IDENTIFIER", "a0"),
    ("IDENTIFIER", "foobar"),
    ("IDENTIFIER", "foo-bar"),
    ("IDENTIFIER", "abc123"),
    ("IDENTIFIER", "LGTM"),
    ("IDENTIFIER", "_"),
    ("IDENTIFIER", "_abc123"),
    ("IDENTIFIER", "abc123_"),
    ("IDENTIFIER", "_abc_123_"),
    ("IDENTIFIER", "_äöü"),
    ("IDENTIFIER", "_本"),
    ("IDENTIFIER", "äöü"),
    ("IDENTIFIER", "本"),
    ("IDENTIFIER", "a۰۱۸"),
    ("IDENTIFIER", "foo६४"),
    ("IDENTIFIER", "bar９８７６"),

    # Heredoc
    ("STRING", "<<EOF\nhello\nworld\nEOF"),
    ("STRING", "<<EOF\nhello world\nEOF"),

    # Strings
    ("STRING", '" "'),
    ("STRING", '"a"'),
    ("STRING", '"本"'),
    ("STRING", '"${file("foo")}"'),
    ("STRING", r'"${file(\"foo\")}"'),
    ("STRING", r'"\a"'),
    ("STRING", r'"\b"'),
    ("STRING", r'"\f"'),
    ("STRING", r'"\n"'),
    ("STRING", r'"\r"'),
    ("STRING", r'"\t"'),
    ("STRING", r'"\v"'),
    ("STRING", r'"\""'),
    ("STRING", r'"\000"'),
    ("STRING", r'"\777"'),
    ("STRING", r'"\x00"'),
    ("STRING", r'"\xff"'),
    ("STRING", r'"\u0000"'),
    ("STRING", r'"\ufA16"'),
    ("STRING", r'"\U00000000"'),
    ("STRING", r'"\U0000ffAB"'),
    ("STRING", '"' + f100 + '"'),

    # Numbers
    ("NUMBER", "0"),
    ("NUMBER", "1"),
    ("NUMBER", "9"),
    ("NUMBER", "42"),
    ("NUMBER", "1234567890"),
    ("NUMBER", "00"),
    ("NUMBER", "01"),
    ("NUMBER", "07"),
    ("NUMBER", "042"),
    ("NUMBER", "01234567"),
    ("NUMBER", "0x0"),
    ("NUMBER", "0x1"),
    ("NUMBER", "0xf"),
    ("NUMBER", "0x42"),
    ("NUMBER", "0x123456789abcDEF"),
    ("NUMBER", "0x" + f100),
    ("NUMBER", "0X0"),
    ("NUMBER", "0X1"),
    ("NUMBER", "0XF"),
    ("NUMBER", "0X42"),
    ("NUMBER", "0X123456789abcDEF"),
    ("NUMBER", "0X" + f100),
    ("NUMBER", "-0"),
    ("NUMBER", "-1"),
    ("NUMBER", "-9"),
    ("NUMBER", "-42"),
    ("NUMBER", "-1234567890"),
    ("NUMBER", "-00"),
    ("NUMBER", "-01"),
    ("NUMBER", "-07"),
    ("NUMBER", "-29"),
    ("NUMBER", "-042"),
    ("NUMBER", "-01234567"),
    ("NUMBER", "-0x0"),
    ("NUMBER", "-0x1"),
    ("NUMBER", "-0xf"),
    ("NUMBER", "-0x42"),
    ("NUMBER", "-0x123456789abcDEF"),
    ("NUMBER", "-0x" + f100),
    ("NUMBER", "-0X0"),
    ("NUMBER", "-0X1"),
    ("NUMBER", "-0XF"),
    ("NUMBER", "-0X42"),
    ("NUMBER", "-0X123456789abcDEF"),
    ("NUMBER", "-0X" + f100),

    # Floats
    ("FLOAT", "0."),
    ("FLOAT", "1."),
    ("FLOAT", "42."),
    ("FLOAT", "01234567890."),
    ("FLOAT", ".0"),
    ("FLOAT", ".1"),
    ("FLOAT", ".42"),
    ("FLOAT", ".0123456789"),
    ("FLOAT", "0.0"),
    ("FLOAT", "1.0"),
    ("FLOAT", "42.0"),
    ("FLOAT", "01234567890.0"),
    ("FLOAT", "-0.0"),
    ("FLOAT", "-1.0"),
    ("FLOAT", "-42.0"),
    ("FLOAT", "-01234567890.0"),

]

@pytest.mark.parametrize("token,input_string", TOKEN_FIXTURES)
def test_tokens(token, input_string):

    print(input_string)

    lexer = hcl.lexer.Lexer()
    lexer.input(input_string)

    lex_tok = lexer.token()

    if lex_tok is None:
        assert token is None
    else:
        assert token == lex_tok.type
        assert lexer.token() is None

# Testing COMMAEND, EPLUS, and EMINUS can't be done on their own since they
# require positive lookbehinds and therefore the lexer will find at least one
# other token
COMPLEX_TOKEN_FIXTURES = [
    # COMMAEND
    (["COMMAEND", "RIGHTBRACKET"], ",]"),
    (["COMMAEND", "RIGHTBRACKET"], ", ]"),

    # EPLUS
    (["FLOAT", "EPLUS"], "0.e"),
    (["FLOAT", "EPLUS"], "1.e+"),
    (["NUMBER", "EPLUS"], "0e"),
    (["NUMBER", "EPLUS"], "0e+"),
    (["FLOAT", "EPLUS"], "1.E"),
    (["FLOAT", "EPLUS"], "1.E+"),
    (["NUMBER", "EPLUS"], "0E"),
    (["NUMBER", "EPLUS"], "1E+"),

    # EMINUS
    (["FLOAT", "EMINUS"], "0.e-"),
    (["NUMBER", "EMINUS"], "1e-"),
    (["FLOAT", "EMINUS"], "0.E-"),
    (["NUMBER", "EMINUS"], "1E-"),
]

@pytest.mark.parametrize("tokens,input_string", COMPLEX_TOKEN_FIXTURES)
def test_complex_tokens(tokens, input_string):

    print(input_string)

    lexer = hcl.lexer.Lexer()
    lexer.input(input_string)

    for tok in tokens:
        lex_tok = lexer.token()

        if lex_tok is None:
            assert tok is None
        else:
            assert tok == lex_tok.type
        print(lex_tok)

    assert lexer.token() is None
