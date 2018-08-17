#!/usr/bin/python
import sys
import argparse
import mysql.connector
import unicodedata


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Query CISBP mysql database")
    parser.add_argument('-s', '-species', dest='species', type=str)
    parser.add_argument('-o', '-fn_output', dest='fn_output', type=str)
    parser.add_argument('--get_cisbp_dbds', action='store_true')
    parsed = parser.parse_args(argv[1:])
    return parsed


def write_fasta(cursor, filename):
    writer = open(filename, "w")
    for item in cursor:
        name = unicodedata.normalize('NFKD', item[0]).encode('ascii', 'ignore')
        seq = unicodedata.normalize('NFKD', item[1]).encode('ascii', 'ignore')
        writer.write(">%s\n%s\n" % (name, seq))
    writer.close()


def write_dbd_fasta(cursor, filename):
    writer = open(filename, "w")
    for item in cursor:
        name = unicodedata.normalize('NFKD', item[0]).encode('ascii', 'ignore')
        start = item[1]
        stop = item[2]
        domain = unicodedata.normalize('NFKD', item[3]).encode('ascii', 'ignore')
        pfam = unicodedata.normalize('NFKD', item[4]).encode('ascii', 'ignore')
        seq = unicodedata.normalize('NFKD', item[5]).encode('ascii', 'ignore')
        writer.write(">%s:%d-%d|%s|%s\n%s\n" % (name, start, stop, domain, pfam, seq))
    writer.close()


def main(argv):
    parsed = parse_args(argv)

    ## connect to CISBP database
    cnx = mysql.connector.connect(user="root", password="", database="cisbp_1_02")
    cursor = cnx.cursor()

    ## query mysql for e.g. Saccharomyces_cerevisiae, Drosophila_melanogaster
    if parsed.get_cisbp_dbds:
        query_dbd = ("SELECT tfs.DBID, prot_features.ProtFeature_FromPos, prot_features.ProtFeature_ToPos, domains.Domain_Name, domains.Pfam_DBID, prot_features.ProtFeature_Sequence FROM tfs JOIN proteins ON tfs.TF_ID = proteins.TF_ID JOIN prot_features ON prot_features.Protein_ID = proteins.Protein_ID JOIN domains ON domains.Domain_ID = prot_features.Domain_ID WHERE tfs.TF_Species = '%s'" % parsed.species)
        cursor.execute(query_dbd)
        write_dbd_fasta(cursor, parsed.fn_output)

    else:
        query_protein = ("SELECT tfs.DBID, proteins.Protein_Sequence FROM tfs INNER JOIN proteins ON tfs.TF_ID = proteins.TF_ID WHERE tfs.TF_Species = '%s'" % parsed.species)
        cursor.execute(query_protein)
        write_fasta(cursor, parsed.fn_output)

    # close connection
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    main(sys.argv)
    