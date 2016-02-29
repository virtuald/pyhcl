#!/bin/bash

pip install -e .
python -m coverage run -m pytest tests
if [ "$?" != "0" ]; then
	exit 1
fi

python -m coverage report -m
