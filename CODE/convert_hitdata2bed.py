#!/usr/bin/python
import sys
import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Convert hitdata to bed format")
    parser.add_argument('-i', '-hitdata', dest='hitdata', type=str)
    parser.add_argument('-o', '-bed', dest='bed', type=str)
    parsed = parser.parse_args(argv[1:])
    return parsed


def load_hitdata(filename):
	f = open(filename, 'r')
	lines = f.readlines()
	f.close()
	return lines


def write_bed(hitdata, filename):
	prev_q_acc = ''
	prev_q_from = ''
	prev_q_to = ''
	dup_counter = 0
	writer = open(filename, 'w')
	for i in range(8, len(hitdata)):
		line = hitdata[i].split()
		query = line[2].strip('>')
		q_from = line[5]
		q_to = line[6]
		q_acc = line[9]
		if q_acc == prev_q_acc and q_from != prev_q_from and q_to != prev_q_to:
			dup_counter += 1
			writer.write('%s\t%s\t%s\t%s\n' % (query, q_from, q_to, query+'.'+q_acc+'-'+str(dup_counter)))
		else:
			dup_counter = 0
			writer.write('%s\t%s\t%s\t%s\n' % (query, q_from, q_to, query+'.'+q_acc))
		prev_q_acc = q_acc
	writer.close()


def main(argv):
	parsed = parse_args(argv)
	write_bed(load_hitdata(parsed.hitdata), parsed.bed)

if __name__ == "__main__":
	main(sys.argv)
