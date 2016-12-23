#
# These tests are taken from hcl/lex_test.go
#

from __future__ import print_function

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

LEX_ERROR_FIXTURES = [
    (
        "old.hcl",
        [
            "IDENTIFIER", "EQUAL", "LEFTBRACE", "STRING", Error
        ],
        "Line 2, column 15"
    ),
    (
        "unterminated_block_comment.hcl",
        [Error],
        "Line 3, column 0"
    ),
    (
        "nested_comment.hcl",
        [Error],
        "Line 5, column 0"
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
def test_lexer(hcl_fname, tokens, error_loc):

    with open(join(LEX_FIXTURE_DIR, hcl_fname), 'r') as fp:
        input = fp.read()

    print(input)

    lexer = hcl.lexer.Lexer()
    lexer.input(input)

    for tok in tokens:
        try:
            lex_tok = lexer.token()
        except ValueError as e:
            assert tok is Error
            assert error_loc in str(e)
            return

        if lex_tok is None:
            assert tok is None
        else:
            assert tok == lex_tok.type
        print(lex_tok)
