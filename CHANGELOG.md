0.2.1 (2016-04-14)
------------------
* Fixes for mutliple configuration blocks with same name

0.2.0 (2016-03-03)
-------------------
* Added support for three tiered structures:

    key1 "key2" "key3" {
        name = value
    }

0.1.15 (2015-10-05)
-------------------
* Fix regression in setup.py
* Remove extra print statement from setup.py

0.1.13 (2015-10-04)
-------------------
* Multi-line comments aren't allowed to terminate with EOF

0.1.12 (2015-10-04)
-------------------
* Move parsetab.dat to build_py step instead of post-install

0.1.11 (2015-04-24)
-------------------
* ply version requirement is now == 3.4

0.1.9 (2015.04.19)
------------------
* Fix unicode error in python 2.x

0.1.8 (2014-11-14)
------------------
* Parse floats properly
* Properly decode \\n
* Complex keys can be set using strings

0.1.6 (2014-10-23)
------------------
* Fix bug that prevented pyhcl from working in a pyinstaller environment

0.1.5 (2014-10-15)
------------------
* Support escaped strings
* Support trailing commas
* Remove support for alternative boolean values

0.1.3 (2014-09-12)
------------------
* Update documentation
* Fix py3 support regarding bytes/strings
* Add tests for bytes and strings
* Support various boolean values

0.1.2 (2014-09-10)
------------------
* Add travis-ci tests, fix minor bugs in setup.py

0.1.0 (2014-09-05)
------------------
* Initial release
