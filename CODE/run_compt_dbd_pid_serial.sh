#!/bin/bash

filepath_protein_list=$1
filepath_fasta=$2
dirpath_output=$3
dirpath_tmp=/tmp/DBD_PIDS

mkdir -p $dirpath_output
mkdir -p $dirpath_tmp


while IFS= read -r protein
do
    if [[ ! -z ${protein} ]]; then
    	echo "... working on" $protein
    	python CODE/compt_dbd_pid.py -q $protein -f $filepath_fasta -o $dirpath_output -t $dirpath_tmp
    fi
done < $filepath_protein_list
