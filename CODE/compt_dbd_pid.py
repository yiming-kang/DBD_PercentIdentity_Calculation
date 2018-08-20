#!/usr/bin/python
import os
import sys
import argparse
import glob
import operator

def parse_args(argv):
	parser = argparse.ArgumentParser(description="This script calculates the DBD percent identity of the query TF to all other TFs. The score is calcualted using Clustalo, and that of each TF-TF pair is the maximal of DBD-DBD pairs.")
	parser.add_argument('-q', '--query_tf', type=str)
	parser.add_argument('-f', '--filepath_fasta', type=str)
	parser.add_argument('-o', '--dir_output', type=str)
	parser.add_argument('-t', '--dir_tmp', type=str)
	parsed = parser.parse_args(argv[1:])
	return parsed


def query_entry(lines):
	## parse fasta header and sequence
	header = lines[0].strip()
	dbd = lines[1].strip()
	protein, pos = header.strip().strip('>').split(':')
	return (header, dbd, protein, pos)


def generate_paired_fasta(query, filepath_fasta, dir):
	## get the dbd sequence of query protein from dbd_fasta file
	f = open(filepath_fasta, "r")
	lines = f.readlines()
	f.close()

	## get indices of query protein and other proteins to pair
	query_indx = [i for i in range(len(lines)/2) if lines[i*2].strip().strip('>').split(':')[0] == query]
	if len(query_indx) == 0:
		sys.exit("No query %s found in fasta file.\n" % query)
	pair_indx = sorted(set(range(len(lines)/2)) - set(query_indx))

	for i in query_indx:
		## parse a protein of interest
		curr_header, curr_dbd, curr_protein, curr_pos = query_entry(lines[i*2:(i+1)*2])
		## link to each of other proteins
		for j in pair_indx: # pair with all seqs
			paired_header, paired_dbd, paired_protein, paired_pos = query_entry(lines[j*2:(j+1)*2])
			## write the sequence pair
			filepath_output = dir +'/'+ '_'.join([curr_protein, curr_pos, paired_protein, paired_pos]) +'.fasta'
			writer = open(filepath_output, 'w') 
			writer.write("%s\n%s\n%s\n%s\n>foo\n%s\n" % (curr_header, curr_dbd, paired_header, paired_dbd, curr_dbd))
			writer.close()


def calculate_pid(dir):
	## use clustalo to calculate pids of all dbd pairs
	pids_dict = {}
	for filepath in glob.glob(dir +'/*.fasta'):
		name = os.path.basename(filepath)
		filepath_out = dir+"/"+name+".out"
		filepath_pidmtr = dir+"/"+name+".pidmtr"
		os.system("clustalo --infile %s --outfile %s --seqtype protein --distmat-out %s --full --percent-id --force" % (filepath, filepath_out, filepath_pidmtr))
		## get pid score
		f = open(filepath_pidmtr, 'r')
		protein, pid = f.readlines()[2].split()[:2]
		protein = protein.split(':')[0]
		pid = float(pid)
		f.close()
		## store max score
		if protein not in pids_dict.keys():
			pids_dict[protein] = []
		pids_dict[protein].append(pid)
	## take max pid of each dbd
	for protein, pids in pids_dict.iteritems():
		pids_dict[protein] = max(pids)
	return pids_dict


def write_pid_adjlst(pids_dict, filepath):
	## sort percent identities and write to file
	sorted_adjlst = sorted(pids_dict.items(), key=operator.itemgetter(1))[::-1]
	f = open(filepath, "w")
	f.write("%s\t%.5f\n" % (os.path.basename(filepath), 100))
	for row in sorted_adjlst:
		f.write("%s\t%.5f\n" % (row[0], row[1]))
	f.close()


def main(argv):
	parsed = parse_args(argv)
	if not os.path.exists(parsed.dir_output):
		sys.exit("Directory not found: %s" % parsed.dir_output)
	if not os.path.exists(parsed.dir_tmp):
		sys.exit("Directory not found: %s" % parsed.dir_tmp)

	dir_tmp = parsed.dir_tmp +'/'+ parsed.query_tf
	if not os.path.exists(dir_tmp):
		os.makedirs(dir_tmp)
	filepath_output = parsed.dir_output+'/'+parsed.query_tf

	generate_paired_fasta(parsed.query_tf, parsed.filepath_fasta, dir_tmp)
	pids = calculate_pid(dir_tmp)
	write_pid_adjlst(pids, filepath_output)


if __name__ == "__main__":
	main(sys.argv)