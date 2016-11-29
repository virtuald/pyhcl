#
# These tests are taken from decoder_test.go
#

from __future__ import print_function

from os.path import join, dirname
import hcl
import json

import pytest

# hcl, json, dict
FIXTURE_DIR = join(dirname(__file__), 'fixtures')
FIXTURES = [
    ('basic.hcl', 'basic.json', None),
    ('basic_squish.hcl', None, {'foo': 'bar', 'bar': '${file("bing/bong.txt")}', 'foo-bar':"baz"}),
    ('decode_policy.hcl', 'decode_policy.json', None),
    ('decode_tf_variable.hcl', 'decode_tf_variable.json', None),
    ('empty.hcl', None, {'resource': {'foo': {}}}),
    ('escape.hcl', None, {'foo': 'bar"baz\\n'}),
    ('flat.hcl', None, {'foo': 'bar', 'Key': 7}),
    ('float.hcl', None, {'a': 1.02}),
    ('float.hcl', 'float.json', None),
    ('multiline_bad.hcl', 'multiline.json', None),
    ('scientific.hcl', 'scientific.json', None),
    ('structure.hcl', 'structure_flat.json', None),
    #('structure2.hcl', 'structure2.json', None),  # not in the golang tests
    ('structure_flatmap.hcl', 'structure_flatmap.json', None),
    ('structure_list.hcl', 'structure_list.json', None), # these don't match in golang either
    ('structure_list.hcl', None, {'foo': [{'key': 7}, {'key': 12}]}), # nor this
    ('issue12.hcl', 'issue12.json', None),
    #'structure_list_deep.json'
    ('structure_multi.hcl', 'structure_multi.json', None),
    ('structure_three_tiers.hcl', 'structure_three_tiers.json', None),
    ('terraform_heroku.hcl', 'terraform_heroku.json', None),
    ('structure_list_deep.hcl','structure_list_deep.json', None)
]




@pytest.mark.parametrize("hcl_fname,json_fname,struct", FIXTURES)
def test_decoder(hcl_fname, json_fname, struct):
    
    with open(join(FIXTURE_DIR, hcl_fname), 'r') as fp:
        hcl_json = hcl.load(fp)
    
    assert json_fname is not None or struct is not None

    if json_fname is not None:
        with open(join(FIXTURE_DIR, json_fname), 'r') as fp:
            good_json = json.load(fp)
        
        assert hcl_json == good_json
    
    if struct is not None:
        assert hcl_json == struct
