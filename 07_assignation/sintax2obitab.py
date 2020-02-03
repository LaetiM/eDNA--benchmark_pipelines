#===============================================================================
#INFORMATIONS
#===============================================================================
"""
CEFE - EPHE - BENCHMARK eDNA  2019
mathon laetitia, guerin pierre-edouard


description:

convert output from SINTAX assignation to obitab


input:

- 


output:

- output.tsv: a tsv file with this header:
"id definition count family_name genus_name species_name sample*"
where sample* is a list of all known samples labels
Each line is a line from assign_vsearch.fasta

usage:

python3 sintax2obitab.py -a assign_vsearch.fasta -o output.tsv

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


listOfLignes = []
##  read vsearch assignement --blast6out
with open(vsearchFile,'r') as readFile:
    for ligne in readFile.readlines():     
        ligneSplit=ligne.split(";")
        thisLigne= Ligne("NA","NA","NA","NA","NA","NA","NA")
        for elem in ligneSplit[1:]:
            thisLigne.id_ligne=str(ligneSplit[0])
            elemSplit=elem.split("=")
            if len(elemSplit) > 1:
                infoTag=elemSplit[0].replace(" ","")
                infoVal=elemSplit[1]
                if infoTag == "merged_sample":
                    exec(elem.replace("\t"," ").replace(" ",""))
                    thisLigne.merged_sample=merged_sample
                elif infoTag == "family_name":
                    thisLigne.family_name=infoVal
                elif infoTag == "genus_name":
                    thisLigne.genus_name=infoVal
                elif infoTag == "species_name":
                    thisLigne.species_name=infoVal
                elif infoTag == "count":
                    thisLigne.count=infoVal
                else:
                    thisLigne.definition="."
                thisLigne.definition="."
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


