#!/bin/sh

echo "Initializing test environment ..."
. ./env

rm -rf tmp
mkdir tmp
cp -f orig_paperwork.conf paperwork.conf
cp -Ra orig_data data

echo "Running tests ..."
nosetests3 -sv "$@"

echo "Done"
