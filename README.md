# DNA binding domain (DBD) Percent Identity Calculation

This module queries the amino acid sequences of the transcription factors (TFs) of interest, searches for the corresponding DNA binding domains (DBDs), aligns each DBD to another, and calculates the percent identity between the algined DBD pair.

### REQUIRED PACKAGES

1. Download and install bedtools as instructed, http://bedtools.readthedocs.io/en/latest/content/installation.html.

2. Downaload and install Clustal Omega as instructed, http://www.clustal.org/omega/.


### CONFIGURE DATABASE [OPTIONAL]

Download and configure CIS-BP database. If you have the amino acid sequences of the TFs from an alternative resource, skip this step.
	
	```
	wget http://cisbp.ccbr.utoronto.ca/data/1.02/DataFiles/SQLDumps/SQLArchive_cisbp_1.02.zip
	unzip SQLArchive_cisbp_1.02.zip
	unzip cisbp_1.02.tfs.zip
	unzip cisbp_1.02.proteins.zip
	unzip cisbp_1.02.domains.zip
	unzip cisbp_1.02.prot_features.zip
	echo "create database `cisbp_1_02`" | mysql -u username -p
	mysql -u username -p cisbp_1_02 < cisbp_1.02.tfs.sql
	mysql -u username -p cisbp_1_02 < cisbp_1.02.proteins.sql
	```

### USAGE

1. Configure tool dependencies
	
	```
	export PATH=/path/to/bedtools/binary:$PATH
	export PATH=/path/to/clustalo/binary:$PATH
	```

2. Download the amino acid sequences of the TFs in the species of interest from online databases, e.g. SGD for yeast or FlyBase for fruit fly. Alternatively, query the sequences in CIS-BP database for a species, e.g. Saccharomyces_cerevisiae or Drosophila_melanogaster. 

	```
	python CODE/query_cisbp_tf_seqs.py -s <species> -o DATA/<species>.tf_aa_seq.fasta
	```

	If you prefer to use DBDs directly from CIS-BP database, enable flag `--get_cisbp_dbds`. Then you may jump to Step 4 without searching for conserved domains.

	```
	python CODE/query_cisbp_tf_seqs.py -s <species> -o DATA/<species>.dbd.fasta --get_cisbp_dbds
	```

3. Upload `<species>.tf_aa_seq.fasta` to NCBI CD-Search Tool, https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi, and submit a job (with default settings) to search for the conserved DBDs. When the search completes, download the domain hits + concise data mode and save as `<species>.dbd_hitdata.txt`. Now use bedtools to parse out the DBD sequences.

	```
	python CODE/convert_hitdata2bed.py -i DATA/<species>.dbd_hitdata.txt -o DATA/<species>.dbd_hitdata.bed
	bedtools getfasta -fi DATA/<species>.tf_aa_seq.fasta -bed DATA/<species>.dbd_hitdata.bed -fo DATA/<species>.dbd.fasta
	```

4. Calculate the pairwised DBD percent identity between two proteins. The maximal percent identity of all DBD-DBD pairs is the score of each protein-protein pair. If SLURM is available for protein-level parallelization, run

	```
	sbatch --array=1-<num_proteins>%32 CODE/run_compt_dbd_pid_parallel.sh <protein_list> DATA/<species>.dbd.fasta DATA/<output_dirpath>
	```

	Otherwise, run serial processing

	```
	bash CODE/run_compt_dbd_pid_serial.sh <protein_list> DATA/<species>.dbd.fasta DATA/<output_dirpath>
	```

5. If there exists an mapping from protein names to TF-encoding gene names, execute the following. It also handles the case the multi-protein to TF mapping by taking the maximal percent identity score. It saves new TF score files and purges the protein score files.

	```
	python CODE/map_proteins2tf.py -f <protein2TF_filepath> -o DATA/<output_dirpath> --purge_protein_score_files
	```

### DESCRIPTION OF RESOURCE FILES

FILENAME | DESCRITPION
--- | ---
DATA/< species >.tf_aa_seq.fasta | TF amino acid sequences. If there are multiple protein systematic names mapped to a gene that encodes the corresponding TF, the identifier of each sequnece is the protein systematic name. For example, FBpp0070062 and FBpp0305207 are mapped to FBgn0040372 according to FlyBase. Otherwise, the identifier is the gene systematic name.
DATA/< species >.protein_list.txt | The list of the sequence identifiers as described above. 
DATA/< species >.protein_tf_conversion.txt | Optional: the table of name conversion between protein sysmenatic names and gene systematic names. First column corresponds to the protein, and second column corresponds to the gene. 

### DESCRIPTION OF OUTPUT FILES

DIRECTORY | DESCRITPION
--- | ---
DATA/< output_dirpath >/ | The directory that contains the percent identifies (PIDs) between each pair of TFs in the genome. Each file titled with a TF's systematic name contains two columns: first column is the TFs that this TF are paired with, and second column is the respective PIDs.

### REFERENCES

Marchler-Bauer A et al. (2015), "CDD: NCBI's conserved domain database.", Nucleic Acids Res.43(D)222-6

Quinlan AR, Hall IM, "BEDTools: a flexible suite of utilities for comparing genomic features", Bioinformatics (2010) 26 (6): 841-842.

Sievers F, Wilm A, Dineen DG, Gibson TJ, Karplus K, Li W, Lopez R, McWilliam H, Remmert M, Söding J, Thompson JD, Higgins DG (2011). Fast, scalable generation of high-quality protein multiple sequence alignments using Clustal Omega. Molecular Systems Biology 7:539 doi:10.1038/msb.2011.75

Weirauch MT, Yang A, Albu M, Cote AG, Montenegro-Montero A, Drewe P, Najafabadi HS, Lambert SA, Mann I, Cook K, Zheng H, Goity A, van Bakel H, Lozano JC, Galli M, Lewsey MG, Huang E, Mukherjee T, Chen X, Reece-Hoyes JS, Govindarajan S, Shaulsky G, Walhout AJ, Bouget FY, Ratsch G, Larrondo LF, Ecker JR, Hughes TR. "Determination and inference of eukaryotic transcription factor sequence specificity.", Cell. 2014 Sep 11;158(6):1431-43. doi: 10.1016/j.cell.2014.08.009.
