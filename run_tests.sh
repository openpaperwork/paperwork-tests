#!/bin/sh

echo "Initializing test environment ..."
export XDG_DATA_HOME=tmp
export GTK_THEME=NonexistingTheme

rm -rf tmp
mkdir tmp
cp -f orig_paperwork.conf paperwork.conf
cp -Ra orig_data data

echo "Running tests ..."
nosetests3 -sv "$@"

echo "Done"
