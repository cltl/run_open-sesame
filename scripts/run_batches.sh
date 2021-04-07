export naf_batches=/mnt/scistor1/group/home/postma/gva/naf_batches
export batches_output=/home/postma/naf_batches_out
export cur_dir=$(pwd)
export open_sesame_dir=/home/postma/run_open-sesame
export frame_to_info=/home/postma/run_open-sesame/dep/frame_to_info.json
export log=${cur_dir}/log

mkdir -p $batches_output 
mkdir -p $log

for batch_dir in $naf_batches/*/
do
    batch=${batch_dir%/}
    [ ! -d $batch ] && echo "Directory /path/to/dir DOES NOT exists."

    basename=$(basename $batch_dir)
    batch_out_dir=${batches_output}/${basename}
    if [ ! -d $batch_out_dir ]
    then
        echo
        echo $(date)
        echo $batch_out_dir    
    fi

    cd $open_sesame_dir
    bash run_open_sesame.sh $batch target-frame $frame_to_info $batch_out_dir > $log/${basename}.out 2> $log/${basename}.err
done
