#!/bin/bash
###############################################################################
## Codes for the paper:
##   ..............
##
## Authors : GUERIN Pierre-Edouard, MATHON Laetitia
## Montpellier 2019-2020
## 
###############################################################################
## Usage:
##    bash 07_assignation/Assign_vsearch.sh
##
## Description:
##  ..............    
##
##
##
###############################################################################
## load config global variables
source 98_infos/config.sh


## Obitools
illuminapairedend=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" illuminapairedend"
obigrep=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obigrep"
ngsfilter=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" ngsfilter"
obisplit=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obisplit"
obiuniq=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obiuniq"
obiannotate=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obiannotate"
obiclean=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obiclean"
ecotag=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" ecotag"
obisort=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obisort"
obitab=${SINGULARITY_EXEC_CMD}" "${OBITOOLS_SIMG}" obitab"

container_python2=${SINGULARITY_EXEC_CMD}" "${EDNATOOLS_SIMG}" python2"



## EDNAtools
vsearch=${SINGULARITY_EXEC_CMD}" "${EDNATOOLS_SIMG}" vsearch"

## Prefix for all generated files
pref="grinder_teleo1"
# Chemin vers r�pertoire contenant les reads forward et reverse
#DATA_PATH='00_Input_data/forward_reverse_reads'

## Prefix of the final table, including the step and the program tested (ie: merging_obitools)
step=assign_vsearch
## Path to the directory containing forward and reverse reads
R1_fastq="$DATA_PATH"/"$pref"/"$pref"_R1.fastq.gz
R2_fastq="$DATA_PATH"/"$pref"/"$pref"_R2.fastq.gz
## path to 'sample_description_file.txt'
sample_description_file=${INPUT_DATA}"/sample_description_file.txt"

# Chemin vers le fichier 'db_sim_teleo1.fasta'
refdb_dir=`pwd`"/07_assignation/db_teleo_vsearch.fasta"


## path to outputs final and temporary (main)
main_dir=`pwd`"/07_assignation/Outputs/01_vsearch/main"
fin_dir=`pwd`"/07_assignation/Outputs/01_vsearch/final"


################################################################################################

## forward and reverse reads assembly
assembly=${main_dir}"/"${pref}".fastq"
$illuminapairedend -r ${R2_fastq} ${R1_fastq} > ${assembly}
## Remove non-aligned reads
assembly_ali="${assembly/.fastq/.ali.fastq}"
$obigrep -p 'mode!="joined"' ${main_dir}"/"${pref}".fastq" > ${assembly_ali}
## Assign each sequence to a sample
identified="${assembly_ali/.ali.fastq/.ali.assigned.fasta}"
unidentified="${assembly_ali/.ali.fastq/_unidentified.fastq}"
$ngsfilter -t ${sample_description_file} -u ${unidentified} ${assembly_ali} --fasta-output > ${identified}
## S�paration du fichier global en un fichier par �chantillon 
$obisplit -p $main_dir/"$pref"_sample_ -t sample --fasta ${identified}


################################################################################################

all_samples_parallel_cmd_sh=$main_dir/"$pref"_sample_parallel_cmd.sh
echo "" > $all_samples_parallel_cmd_sh
for sample in `ls $main_dir/"$pref"_sample_*.fasta`;
do
sample_sh="${sample/.fasta/_cmd.sh}"
echo "bash "$sample_sh >> $all_samples_parallel_cmd_sh
# D�r�plication des reads en s�quences uniques
dereplicated_sample="${sample/.fasta/.uniq.fasta}"
echo $obiuniq" -m sample "$sample" > "$dereplicated_sample > $sample_sh;
# On garde les s�quences de plus de 20pb sans bases ambigues
good_sequence_sample="${dereplicated_sample/.fasta/.l20.fasta}"
echo $obigrep" -s '^[ACGT]+$' -l 20 "$dereplicated_sample" > "$good_sequence_sample >> $sample_sh
# Supression des erreurs de PCR et s�quen�age (variants)
clean_sequence_sample="${good_sequence_sample/.fasta/.r005.clean.fasta}"
echo $obiclean" -r 0.05 -H "$good_sequence_sample" > "$clean_sequence_sample >> $sample_sh
done
parallel < $all_samples_parallel_cmd_sh
# Concatenation de tous les �chantillons en un fichier
all_sample_sequences_clean=$main_dir/"$pref"_all_sample_clean.fasta
cat $main_dir/"$pref"_sample_*.uniq.l20.r005.clean.fasta > $all_sample_sequences_clean
# D�r�plication en s�quences uniques
all_sample_sequences_uniq="${all_sample_sequences_clean/.fasta/.uniq.fasta}"
$obiuniq -m sample $all_sample_sequences_clean > $all_sample_sequences_uniq
# Supression des attributs inutiles dans l'ent�te des s�quences
all_sample_sequences_ann="${all_sample_sequences_uniq/.fasta/.ann.fasta}"
$obiannotate  --delete-tag=scientific_name_by_db --delete-tag=obiclean_samplecount --delete-tag=obiclean_count --delete-tag=obiclean_singletoncount \
 --delete-tag=obiclean_cluster --delete-tag=obiclean_internalcount --delete-tag=obiclean_head  --delete-tag=obiclean_headcount \
 --delete-tag=id_status --delete-tag=rank_by_db --delete-tag=obiclean_status --delete-tag=seq_length_ori --delete-tag=sminL --delete-tag=sminR \
 --delete-tag=reverse_score --delete-tag=reverse_primer --delete-tag=reverse_match --delete-tag=reverse_tag --delete-tag=forward_tag --delete-tag=forward_score \
 --delete-tag=forward_primer --delete-tag=forward_match --delete-tag=tail_quality --delete-tag=mode --delete-tag=seq_a_single --delete-tag=status \
 --delete-tag=direction --delete-tag=seq_a_insertion --delete-tag=seq_b_insertion --delete-tag=seq_a_deletion --delete-tag=seq_b_deletion \
 --delete-tag=ali_length --delete-tag=head_quality --delete-tag=seq_b_single $all_sample_sequences_uniq > $all_sample_sequences_ann
# Tri des s�quences par 'count'
all_sample_sequences_sort="${all_sample_sequences_ann/.fasta/.sort.fasta}"
$obisort -k count -r $all_sample_sequences_ann > $all_sample_sequences_sort
# Assignation taxonomique
all_sample_sequences_vsearch_tag="${all_sample_sequences_sort/.fasta/.tag.vsearch}"
$vsearch --usearch_global $all_sample_sequences_sort --db $refdb_dir --notrunclabels --id 0.8 --fasta_width 0 --top_hits_only --blast6out $all_sample_sequences_vsearch_tag
## convert vsearch assignation file into obifasta
all_sample_sequences_vsearch_tag_obifasta="${all_sample_sequences_vsearch_tag/.vsearch/.vsearch.fasta}"
$container_python2 07_assignation/convert_assign_vsearch_2_obifasta.py -f $all_sample_sequences_sort -a $all_sample_sequences_vsearch_tag -o $all_sample_sequences_vsearch_tag_obifasta
## Create final table
$obitab -o $all_sample_sequences_vsearch_tag_obifasta > $fin_dir/"$step"

################################################################################################

#gzip $main_dir/*