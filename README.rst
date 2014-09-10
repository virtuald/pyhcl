pyhcl
=====

|Build Status|

Implements a parser for `HCL (HashiCorp Configuration
Language) <https://github.com/hashicorp/hcl>`__ in Python. This
implementation aims to be compatible with the original golang version of
the parser.

The grammar and many of the tests/fixtures were copied/ported from the
golang parser into pyhcl.

Installation
============

::

    pip install pyhcl

Usage
=====

This module is intended to be used in mostly the same way that one would
use the json module in python, and load/loads/dumps are implemented.

::

    import hcl

    with open('file.hcl', r) as fp:
        obj = hcl.load(fp)

Currently the dumps function outputs JSON, and not HCL.

Syntax
======

-  Single line comments start with ``#`` or ``//``

-  Multi-line comments are wrapped in ``/*`` and ``*/``

-  Values are assigned with the syntax ``key = value`` (whitespace
   doesn't matter). The value can be any primitive: a string, number,
   boolean, object, or list.

-  Strings are double-quoted and can contain any UTF-8 characters.
   Example: ``"Hello, World"``

-  Numbers are assumed to be base 10. If you prefix a number with 0x, it
   is treated as a hexadecimal. If it is prefixed with 0, it is treated
   as an octal. Numbers can be in scientific notation: "1e10".

-  Boolean values: ``true``, ``false``, ``on``, ``off``, ``yes``,
   ``no``.

-  Arrays can be made by wrapping it in ``[]``. Example:
   ``["foo", "bar", 42]``. Arrays can contain primitives and other
   arrays, but cannot contain objects. Objects must use the block syntax
   shown below.

Objects and nested objects are created using the structure shown below::

    variable "ami" {
        description = "the AMI to use"
    }

Testing
=======

To run the tests::

    pip install -r testing-requirements.txt
    tests/run_tests.sh

Authors
=======

Dustin Spicuzza (dustin@virtualroadside.com)

Note: This project is not associated with Hashicorp

.. |Build Status| image:: https://travis-ci.org/virtuald/pyhcl.svg
   :target: https://travis-ci.org/virtuald/pyhcl
