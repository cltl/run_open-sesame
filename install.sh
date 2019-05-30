#!/usr/bin/env bash

rm -rf resources
mkdir resources
cd resources
git clone https://github.com/swabhs/open-sesame

echo "Please follow the installation instructions in the README of open-sesame"
echo "It is written using Python 2.7"
echo "Please download language model for spacy using for example 'python -m spacy download en'"
