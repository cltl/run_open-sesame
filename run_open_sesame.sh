#!/usr/bin/env bash

if [ $# -eq 0 ];
    then
    echo
    echo "Usage:                  : $0 naf_folder tasks frame_to_info"
    echo
    exit -1;
fi

here=$(pwd)

out_folder="output" # where do you want to store the output?
naf_folder=$1 #where is the input folder with NAF files?
tasks=$2
frame_to_info=$3
sesame_commit="96639aedd24442433365d4d9fca877931fe222e4" # which commit of open sesame did you use?
input=$here/$out_folder/all_sentences.txt
output=$here/$out_folder/all_sentences.conll

python convert_naf_to_input_open_sesame.py --input_folder=$naf_folder --languages="en" --output_folder=$out_folder --verbose=1

cd scripts
bash prediction_on_unseen_data.sh $input $tasks $output > ../$out_folder/log.out 2> ../$out_folder/log.err
cd ..

python update_naf_with_open_sesame_output.py --naf_folder=$naf_folder --output_open_sesame=$out_folder --path_frame_to_info=$frame_to_info --commit=$sesame_commit --verbose=1
