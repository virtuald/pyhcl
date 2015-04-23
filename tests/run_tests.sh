#!/bin/bash

cd `dirname $0`
python -m coverage run --source hcl -m pytest $@
if [ "$?" != "0" ]; then
	exit 1
fi

python -m coverage report -m
