#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH -D ./
#SBATCH -o LOG/log_%A_%a.out
#SBATCH -e LOG/log_%A_%a.err
#SBATCH -J dbd_pids


filepath_protein_list=$1
filepath_fasta=$2
dirpath_output=$3
dirpath_tmp=/tmp/DBD_PIDS

mkdir -p $dirpath_output
mkdir -p $dirpath_tmp

read protein < <( sed -n ${SLURM_ARRAY_TASK_ID}p $filepath_protein_list )
set -e

if [[ ! -z ${protein} ]]; then
	echo "... working on" $protein
	python CODE/compt_dbd_pid.py -q $protein -f $filepath_fasta -o $dirpath_output -t $dirpath_tmp
fi
