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
        "old.hcl",
        [
            "IDENTIFIER", "EQUAL", "LEFTBRACE", "STRING", Error
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
    (
        "unterminated_block_comment.hcl",
        [Error]
    )
]

@pytest.mark.parametrize("hcl_fname,tokens", LEX_FIXTURES)
def test_lexer(hcl_fname, tokens):
    
    with open(join(LEX_FIXTURE_DIR, hcl_fname), 'r') as fp:
        input = fp.read()
    
    print(input)
    
    lexer = hcl.lexer.Lexer()
    lexer.input(input)

    for tok in tokens:
        try:
            lex_tok = lexer.token()
        except ValueError:
            assert tok is Error
            return
            
        if lex_tok is None:
            assert tok is None
        else:
            assert tok == lex_tok.type 
        print(lex_tok)
            
    assert lexer.token() is None

