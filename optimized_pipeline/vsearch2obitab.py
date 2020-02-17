#===============================================================================
#INFORMATIONS
#===============================================================================
"""
CEFE - EPHE - BENCHMARK eDNA  2019
mathon laetitia, guerin pierre-edouard


description:

convert output from vsearch assignation to obitab


input:

- assign_vsearch.fasta: a fasta files generated by assignation vsearch command


output:

- output.tsv: a tsv file with this header:
"id definition count family_name genus_name species_name sample*"
where sample* is a list of all known samples labels
Each line is a line from assign_vsearch.fasta

usage:

python3 vsearch2obitab.py -a assign_vsearch.fasta -o output.tsv

"""
#===============================================================================
#MODULES
#===============================================================================
import argparse
import os


#===============================================================================
#CLASS
#===============================================================================

class Ligne:
    def __init__(self,id_ligne,merged_sample,family_name,genus_name,species_name,definition,count):
        self.id_ligne = id_ligne
        self.merged_sample= merged_sample
        self.family_name = family_name
        self.genus_name = genus_name
        self.species_name = species_name
        self.definition = definition
        self.count = count
    def fill_missing_keys(self, all_keys):
        for key in all_keys:
            if key not in self.merged_sample.keys():
                self.merged_sample[key]=0
        for key in all_keys:
            self.merged_sample[key] = self.merged_sample.pop(key)



#===============================================================================
#ARGUMENTS
#===============================================================================

parser = argparse.ArgumentParser('convert fasta to obiconvert format')
parser.add_argument("-o","--output",type=str)
parser.add_argument("-a","--vsearch_assignation",type=str)



#===============================================================================
#MAIN
#===============================================================================

args = parser.parse_args()
vsearchFile = args.vsearch_assignation
outputFile = args.output


#vsearchFile="07_assignation/test/assign_vsearch.fasta"
#outputFile="07_assignation/test/tabfin.tsv"

#vsearchFile= "07_assignation/Outputs/01_vsearch/main/grinder_teleo1_all_sample_clean.uniq.ann.sort.uniqid.tag.fasta"
vsearchFile="/share/reservebenefit/working/pierre/eDNA--benchmark_pipelines/optimized_pipeline/Outputs/main/grinder_teleo1_all_sample_clean.ann.sort.uniqid.tag.preformat.fasta"

listOfLignes = []
listOfIds = []
newId=1 # 1 -> this Id is new 0 -> this Id is already known

##  read vsearch assignement --blast6out
with open(vsearchFile,'r') as readFile:
    for ligne in readFile.readlines():
        ligneSplit=ligne.split(";")
        thisLigne= Ligne("NA","NA","NA","NA","NA","NA","NA")
        thisLigne.id_ligne=str(ligneSplit[0].split(" ")[0].replace(">",""))
        if thisLigne.id_ligne not in listOfIds:
            listOfIds.append(thisLigne.id_ligne)
            newId=1
            if "count" in ligneSplit[0]:
                thisCount=ligneSplit[0].split("=")[1]
                thisLigne.count=thisCount
            for elem in ligneSplit[1:]:
                elemSplit=elem.split("=")
                if len(elemSplit) > 1:
                    infoTag=elemSplit[0].replace(" ","")
                    infoVal=elemSplit[1]
                    if infoTag == "merged_sample":
                        exec(elem.replace("\t"," ").replace(" ",""))
                        thisLigne.merged_sample=merged_sample
                    elif infoTag == "count":
                        thisLigne.count=infoVal
                    elif infoTag == "family_name":
                        thisLigne.family_name=infoVal
                    elif infoTag == "genus_name":
                        thisLigne.genus_name=infoVal
                    elif infoTag == "species_name":
                        thisLigne.species_name=infoVal
                    else:
                        thisLigne.definition="."
                    thisLigne.definition="."
        else:
            newId=0
            for i in range(len(listOfLignes)):
                if listOfLignes[i].id_ligne == thisLigne.id_ligne:
                    for elem in ligneSplit[1:]:            
                        elemSplit=elem.split("=")
                        if len(elemSplit) > 1:
                            infoTag=elemSplit[0].replace(" ","")
                            infoVal=elemSplit[1]                    
                            if infoTag == "family_name":
                                if listOfLignes[i].family_name != infoVal:                            
                                    listOfLignes[i].family_name = listOfLignes[i].family_name + ',' +infoVal
                            elif infoTag == "genus_name":
                                if listOfLignes[i].genus_name != infoVal:                   
                                    listOfLignes[i].genus_name = listOfLignes[i].genus_name + ',' +infoVal
                            elif infoTag == "species_name":
                                if listOfLignes[i].species_name != infoVal:                   
                                    listOfLignes[i].species_name = listOfLignes[i].species_name + ',' +infoVal
                            else:
                                listOfLignes[i].definition="r"
        if newId:
            listOfLignes.append(thisLigne)



## get all keys of sample from merged_sample dic
all_keys = list(set().union(*(d.merged_sample.keys() for d in listOfLignes)))


## add zero value to each missing keys into merged_sample dic for each line
for ligne in listOfLignes:
    ligne.fill_missing_keys(all_keys) 

## write the final table
sourceFile= open(outputFile,"w+")
### write header
print("id","definition","count","family_name","genus_name","species_name",*[key for key in all_keys],sep="\t",file=sourceFile)
### write line content
for ligne in listOfLignes:
    print(ligne.id_ligne,ligne.definition,ligne.count,ligne.family_name,ligne.genus_name,ligne.species_name,*[ligne.merged_sample[key] for key in all_keys ],sep="\t",file=sourceFile)

sourceFile.close()


