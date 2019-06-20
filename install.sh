#!/usr/bin/env bash


rm -r spacy_to_naf.py
wget https://raw.githubusercontent.com/cltl/SpaCy-to-NAF/master/spacy_to_naf.py

rm -rf resources
mkdir resources
cd resources
git clone https://github.com/swabhs/open-sesame

echo "Please follow the installation instructions in the README of open-sesame"
echo "It is written using Python 2.7"