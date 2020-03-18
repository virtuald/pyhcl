#
# These tests are taken from hcl/parse_test.go
#

from __future__ import print_function

from os.path import join, dirname
import hcl
import json

import pytest

PARSE_FIXTURE_DIR = join(dirname(__file__), 'lex-fixtures')
PARSE_FIXTURES = [
    (
        "assign_colon.hcl",
        False,
    ),
    (
        "comment.hcl",
        False,
    ),
    (
        "list_comma.hcl",
        False,
    ),
    (
        "list_of_maps.hcl",
        False,
    ),
    (
        "multiple.hcl",
        False,
    ),
    (
        "structure.hcl",
        False,
    ),
    (
        "structure_basic.hcl",
        False,
    ),
    (
        "structure_empty.hcl",
        False,
    ),
    (
        "complex.hcl",
        False,
    ),
    (
        "assign_deep.hcl",
        False,
    ),
    (
        "types.hcl",
        False,
    ),
    (
        "structure_comma.hcl",
        False,
    ),
    (
        "terraform0.12syntax.hcl",
        False,
    ),
    (
        "conditional_operator.hcl",
        False,
    ),
]

@pytest.mark.parametrize("export_comments", [None, 'LINE', 'MULTILINE', 'ALL'])
@pytest.mark.parametrize("hcl_fname,invalid", PARSE_FIXTURES)
def test_parser_bytes(hcl_fname, invalid, export_comments):
    
    with open(join(PARSE_FIXTURE_DIR, hcl_fname), 'rb') as fp:
        
        input = fp.read()
        print(input)
        
        if not invalid:
            hcl.loads(input, export_comments)
        else:
            with pytest.raises(ValueError):
                hcl.loads(input, export_comments)
                
@pytest.mark.parametrize("export_comments", [None, 'LINE', 'MULTILINE', 'ALL'])
@pytest.mark.parametrize("hcl_fname,invalid", PARSE_FIXTURES)
def test_parser_str(hcl_fname, invalid, export_comments):
    
    with open(join(PARSE_FIXTURE_DIR, hcl_fname), 'r') as fp:
        
        input = fp.read()
        print(input)
        
        if not invalid:
            hcl.loads(input, export_comments)
        else:
            with pytest.raises(ValueError):
                hcl.loads(input, export_comments)
