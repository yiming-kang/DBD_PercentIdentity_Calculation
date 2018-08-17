#!/usr/bin/python
import os
import sys
import argparse
import glob
import operator

def parse_args(argv):
	parser = argparse.ArgumentParser(description="This script maps the protein names of percent identity adjcency list to the TF names. The score of each TF-TF pair is the maximal of all protein-protein pairs, if multiple proteins map to each TF. Filenames will be updated as well.")
	parser.add_argument('-f', '--filepath_prot2tf', type=str)
	parser.add_argument('-o', '--dir_pids', type=str)
	parser.add_argument('--purge_protein_score_files', action='store_true')
	parsed = parser.parse_args(argv[1:])
	return parsed


def get_prot2tf(filepath):
	## get the proteins to tf conversion
	prot2tf = {}
	f = open(filepath, "r")
	for line in f.readlines():
		protein, tf = line.strip().split("\t")
		prot2tf[protein] = tf
	return prot2tf


def check_prot2tf(prot2tf, protein):
	if protein not in prot2tf.keys():
		sys.exit("Protein %s does not have a matched TF in conversion. Aborted mapping. Please update the conversion file." % protein)


def update_pids(prot2tf, dir, purge=False):
	## initialize pids dict
	pids_dict = {}
	for tf in prot2tf.values():
		pids_dict[tf] = {}
	## iterate through all proteins with pids calculated
	protein_filepaths = glob.glob(dir+"/*")
	for filepath in protein_filepaths:
		protein = os.path.basename(filepath)
		check_prot2tf(prot2tf, protein)
		## dump data into pid dict
		tf = prot2tf[protein]
		f = open(filepath, "r")
		for line in f.readlines():
			paired_prot, pid = line.strip().split("\t")
			paired_tf = prot2tf[paired_prot]
			if paired_tf not in pids_dict[tf]:
				pids_dict[tf][paired_tf] = []
			pids_dict[tf][paired_tf].append(float(pid))
	## save max pids for tfs
	for tf in pids_dict.keys():
		for paired_tf, pids in pids_dict[tf].iteritems():
			pids_dict[tf][paired_tf] = max(pids)
		filepath_output = dir +'/'+ tf
		write_pid_adjlst(pids_dict[tf], filepath_output)
	## delete protein pid files
	if purge:
		for filepath in protein_filepaths:
			os.system("rm %s" % filepath)


def write_pid_adjlst(pids_dict, filepath):
	## sort percent identities and write to file
	sorted_adjlst = sorted(pids_dict.items(), key=operator.itemgetter(1))[::-1]
	f = open(filepath, "w")
	for row in sorted_adjlst:
		f.write("%s\t%.5f\n" % (row[0], row[1]))
	f.close()


def main(argv):
	parsed = parse_args(argv)
	if not os.path.exists(parsed.filepath_prot2tf):
		sys.exit("File not found: %s" % parsed.filepath_prot2tf)
	if not os.path.exists(parsed.dir_pids):
		sys.exit("Directory not found: %s" % parsed.dir_pids)

	prot2tf = get_prot2tf(parsed.filepath_prot2tf)
	update_pids(prot2tf, parsed.dir_pids, purge=parsed.purge_protein_score_files)


if __name__ == "__main__":
	main(sys.argv)