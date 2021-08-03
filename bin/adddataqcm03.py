#!/usr/bin/env python3

# Add meta-data to a LaTeX file of questions
# Usage : 'python3 adddataqcm.py toto.tex'
# Output : create a tex toto_data.tex

import argparse
import re
import sys
import os


#--------------------------------------------------
#--------------------------------------------------
# Arguments 

parser = argparse.ArgumentParser(description='Add meta-data to a mutliple choice questions LaTeX file.')
parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true', default=False, help='overwrite existing data')
#parser.add_argument('--author', nargs='?', help='name of the author(s)')
parser.add_argument('--num', nargs='?', help='start value of the counter qnum')
parser.add_argument('inputfile', help='input LaTeX filename')
parser.add_argument('outputfile', nargs='?', help='output Latex filename')

options = parser.parse_args()

#print(options.overwrite)
#print(options.inputfile)
#print(options.outputfile)

#sys.exit(0)

is_overwrite = options.overwrite
option_num = options.num
latex_file = options.inputfile
output = options.outputfile

# Get argument : a tex file
file_name, file_extension = os.path.splitext(latex_file) 

# Output file name 
if output:
    output_file = output    # Name given by user
else:
    output_file = file_name+'_data'+'.tex' # If no name add a '_data.tex' extension


# Read file object to string
fic = open(latex_file, 'r', encoding='utf-8')
text_all = fic.read()
fic.close()




#--------------------------------------------------
# Add data to one LaTeX exercice
def add_data_one_exo(text_exo,**kwargs):
    
    new_text_exo = text_exo 

    # The title : search the title, if any (and remove it from the question)
    thetitle = re.search(r'^(\s*)\[(.*?)\]',new_text_exo, flags=re.MULTILINE|re.DOTALL)
    if thetitle:
        title = thetitle.group(0)
        #title = re.sub("[\[\]]","",title, flags=re.MULTILINE|re.DOTALL)
        #print('\n\n---title---\n'+title+'\n\n')
        new_text_exo = re.sub(r"^(\s*)\[(.*?)\]","",new_text_exo, flags=re.MULTILINE|re.DOTALL)
    else:
        title = ""

#    # the classification
#    if classif:
#        new_text_exo = "\n\\qclassification{" + classif + "}" + new_text_exo

#    # the section
#    thesection = re.search('(?<=\\\\qsection\{)(.*?)(?=\})',new_text_exo, flags=re.MULTILINE|re.DOTALL)

#    if thesection and is_overwrite:  # overwrite an existing section
#        new_section = "\\qauthor{"+option_author+"}"
#        new_text_exo = re.sub("\\\\qauthor\{(.*?)\}",new_author,new_text_exo, flags=re.MULTILINE|re.DOTALL)

    # the current subsection
    if ('subsection' in kwargs) and kwargs['subsection']:
        thesubsection = re.search(r'(?<=\\qsubsection\{)(.*?)(?=\})',new_text_exo, flags=re.MULTILINE|re.DOTALL)
        if thesubsection:  # overwrite an existing subsection
            new_subsection = r"\qsubsection{" + kwargs['subsection'] + "}"
            new_text_exo = re.sub(r"\\qsubsection\{(.*?)\}",new_subsection,new_text_exo, flags=re.MULTILINE|re.DOTALL)
        else: # new subsection
            new_text_exo = r"\qsubsection{" + kwargs['subsection'] + "}" + new_text_exo

    # the current section
    if ('section' in kwargs) and kwargs['section']:
        thesection = re.search(r'(?<=\\qsection\{)(.*?)(?=\})',new_text_exo, flags=re.MULTILINE|re.DOTALL)
        if thesection:  # overwrite an existing section
            new_section = r"\qsection{" + kwargs['section'] + "}"
            new_text_exo = re.sub(r"\\qsection\{(.*?)\}",new_section,new_text_exo, flags=re.MULTILINE|re.DOTALL)
        else: # new section
            new_text_exo = r"\qsection{" + kwargs['section'] + "}" + "\n"  + new_text_exo

    # the author
    if ('author' in kwargs) and kwargs['author']:
        theauthor = re.search(r'(?<=\\qauthor\{)(.*?)(?=\})',new_text_exo, flags=re.MULTILINE|re.DOTALL)
        if theauthor:  # overwrite an existing author
            new_author = r"\qauthor{" + kwargs['author'] + "}"
            new_text_exo = re.sub(r"\\qauthor\{(.*?)\}",new_author,new_text_exo, flags=re.MULTILINE|re.DOTALL)
        else: # new author
            new_text_exo = r"\qauthor{" + kwargs['author'] + "}" + "\n" + new_text_exo

    # the counter qnum
    thenum = re.search(r'(?<=\\qnum\{)(.*?)(?=\})',new_text_exo, flags=re.MULTILINE|re.DOTALL)

    if thenum and is_overwrite and kwargs['num']:  # overwrite an existing numerotation
        new_num = r"\qnum{"+str(kwargs['num'])+"}"
        new_text_exo = re.sub(r"\\qnum\{(.*?)\}",new_num,new_text_exo, flags=re.MULTILINE|re.DOTALL)

    if (not thenum) and option_num and kwargs['num'] : # new author
        new_text_exo = r"\qnum{"+str(kwargs['num'])+"}"+new_text_exo

    title = title+"\n"
    new_text_exo = r"\begin{question}" + title + new_text_exo + r"\end{question}"
   
    return new_text_exo


#--------------------------------------------------
#--------------------------------------------------
# Find the author
myauthor = re.search(r'\\qcmauthor\{(.*?)\}',text_all, flags=re.MULTILINE|re.DOTALL)
if myauthor:
    myauthor = myauthor.group(1)
    #print('Author : '+myauthor)

#--------------------------------------------------
#--------------------------------------------------
# Find sections and subsections
list_all_section = list(re.finditer(r'\\section\{(.*?)\}',text_all, flags=re.MULTILINE|re.DOTALL))
list_all_subsection = list(re.finditer(r'\\subsection\{(.*?)\}',text_all, flags=re.MULTILINE|re.DOTALL))


# for section in list_all_section:   
#     print('---- Section ---- Position %02d-%02d\n %s' % (section.start(), section.end(), section.group(1)))

# for subsection in list_all_subsection:    
#     print('---- Subsection ---- Position %02d-%02d\n %s' % (subsection.start(), subsection.end(), subsection.group(1)))

#--------------------------------------------------
#--------------------------------------------------
# Split into each exercices

list_all_exo = list(re.finditer(r'\\begin\{question\}(.*?)\\end\{question\}',text_all, flags=re.MULTILINE|re.DOTALL))
new_text_all = text_all

if option_num:
    numexo = int(option_num)
else:
    numexo = 1


# Reverse the indices: end to the start
numexo = numexo + len(list_all_exo) - 1

for exo in reversed(list_all_exo):    # start from the end to keep line number replacement
    #print('---- Lines %02d-%02d\n %s' % (exo.start(), exo.end(), exo.group(0)))
    #print('---- Exo ---- Position %02d-%02d\n' % (exo.start(), exo.end()))
    old_exo = exo.group(1)

    # find the current section
    mysection = None
    for section in list_all_section:
        if section.start() < exo.start():
            mysection = section.group(1) 

    # find the current subsection
    mysubsection = None
    for subsection in list_all_subsection:
        if subsection.start() < exo.start():
            mysubsection = subsection.group(1) 

    # Make the transformation of one exercise
    new_exo = add_data_one_exo(old_exo,num=numexo,author=myauthor,section=mysection,subsection=mysubsection)

    new_text_all = new_text_all[:exo.start()] + new_exo + new_text_all[exo.end():]
    numexo = numexo - 1

with open(output_file, 'w', encoding='utf-8') as out:  
   out.write(new_text_all)







