#!/bin/sh

echo "Initializing test environment ..."
. ./env

rm -rf tmp
rm -rf data
rm -rf paperwork.conf

mkdir tmp

cp -f orig_paperwork.conf paperwork.conf
cp -Ra orig_data data

echo "Running tests ..."
nosetests3 -sv "$@"
res=$?

echo "Done"

exit ${res}
