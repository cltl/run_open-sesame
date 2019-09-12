#!/usr/bin/env bash
#check if enough arguments are passed, else print usage information
if [ $# -eq 0 ];
then
    echo
    echo "Usage:                    : $0 input_path output_path"
    echo
    echo "input_path                : input_path (absolute path)"
    echo "tasks                     : target-frame | target-frame-argid"
    echo "output_path               : output_path (absolute path)"
    echo "bash prediction_on_unseen_data.sh $(readlink -f ../output/all_sentences.txt) $(readlink -f ../output/all_sentences.conll)"
    exit -1;
fi

input_path=$1
tasks=$2
output_path=$3

cd ../resources/open-sesame

python2 -m sesame.targetid --mode predict \
                          --model_name fn1.7-pretrained-targetid \
                          --raw_input $input_path

python2 -m sesame.frameid --mode predict \
                         --model_name fn1.7-pretrained-frameid \
                         --raw_input logs/fn1.7-pretrained-targetid/predicted-targets.conll

if [ "$tasks" == "target-frame" ]; then
    cp logs/fn1.7-pretrained-frameid/predicted-frames.conll $output_path
fi

if [ "$tasks" == "target-frame-argid" ]; then
    python2 -m sesame.argid --mode predict \
                            --model_name fn1.7-pretrained-argid \
                            --raw_input logs/fn1.7-pretrained-frameid/predicted-frames.conll

    cp logs/fn1.7-pretrained-argid/predicted-args.conll $output_path
fi
