MODEL=targetid
MODEL_NAME=fn1.7-pretrained-targetid

cd ../resources/open-sesame/
python2 -m sesame.$MODEL --mode test --model_name $MODEL_NAME
