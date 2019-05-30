MODEL=argid
MODEL_NAME=fn1.7-pretrained-argid

cd ../resources/open-sesame/
python2 -m sesame.$MODEL --mode train --model_name $MODEL_NAME
