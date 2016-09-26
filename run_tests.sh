#!/bin/sh

rm -rf tmp
mkdir tmp

export XDG_DATA_HOME=tmp

cp -f orig_paperwork.conf paperwork.conf

nosetests3 -sv tests

rm -f paperwork.conf  # to avoid confusion
