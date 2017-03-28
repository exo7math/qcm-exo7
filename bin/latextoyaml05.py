#!/usr/bin/env python3

# Convert a LaTeX file to yaml file
# Usage : 'python3 latextoyaml.py toto.tex'
# Output : create a file toto.yaml

import argparse
import re
import sys
import os


#--------------------------------------------------
#--------------------------------------------------
# Arguments 

parser = argparse.ArgumentParser(description='Conversion of mutliple choice questions from LaTeX to the yaml format.')
parser.add_argument('inputfile', help='input LaTeX filename')
parser.add_argument('outputfile', nargs='?', help='output yaml filename')

options = parser.parse_args()

#print(options.inputfile)
#print(options.outputfile)


latex_file = options.inputfile
output = options.outputfile

# Get argument : a tex file
file_name, file_extension = os.path.splitext(latex_file) 

# Output file name 
if output:
    yaml_file = output    # Name given by user
else:
    yaml_file = file_name+'.yaml' # If no name add a .yaml extension


# Read file object to string
fic = open(latex_file, 'r', encoding='utf-8')
text_all = fic.read()
fic.close()

#--------------------------------------------------
# Add indentation at each line
def add_space(text):
    indent = ' '*8
    #re.sub(r'^[^a]*','')
    #print('Before\n'+text)
    spacetext = re.sub('^[\s]*','',text,flags=re.MULTILINE) # Delete potential space at the beginning
    #print('After\n'+text)
    spacetext = indent+spacetext  # First line
    spacetext = re.sub('\n','\n'+indent,spacetext,flags=re.MULTILINE) # Add indentation
    return spacetext

# Test
#mytext = 'Ici Londres\nLes français\n\nparlent aux français'
#spacetext = add_space(mytext)
#print(mytext)
#print(spacetext) 


#--------------------------------------------------
# Convert a text with dollars to text with \( \) or \[ \]
def dollars_to_tags(text):
    # Substitute $$ to \[ \]
    text2 = re.sub("\$\$(.+?)\$\$","\\\[\g<1>\\\]",text, flags=re.MULTILINE|re.DOTALL)
    # Substitute $ to \( \)
    text1 = re.sub("\$(.+?)\$","\\\(\g<1>\\\)",text2, flags=re.MULTILINE|re.DOTALL)
    return text1

# Test
#text = "Voici $2+2$ qui fait $$4$$. Et voici une formule $$\int f(x) dx$$."
#newtext = dollars_to_tags(text)
#print('\n\n----------------')
#print('\n\n'+text)
#print('\n\n'+newtext)


#--------------------------------------------------
# Convert one LaTeX exercice to a yaml block
def one_exo_to_yaml(text_exo):

    # delete the comments all the end of a line after a '%'
    text_exo = re.sub("%(.*)","",text_exo,flags=re.MULTILINE)

#    # Find the id
#    theid = re.search('(?<=\{)([0-9]+)',text_exo)
#    id = int(theid.group(0))

    # First convert dollars to tags
    text_exo = dollars_to_tags(text_exo)

    # Find the question and options
    theallquestion = re.search('(.*?)(?=[\s*]\\\\begin{answers})',text_exo, flags=re.MULTILINE|re.DOTALL)
    allquestion = theallquestion.group(0)
    allquestion = re.sub("\s+\Z","",allquestion, flags=re.MULTILINE|re.DOTALL)
    #print('\n\n---question---\n'+allquestion+'\n\n')


    # The title : search the title (and remove it from the question)
    thetitle = re.search('^(\s*)\[(.*?)\]',allquestion, flags=re.MULTILINE|re.DOTALL)
    if thetitle:
        title = thetitle.group(0)
        title = re.sub("[\[\]]","",title, flags=re.MULTILINE|re.DOTALL)
        #print('\n\n---title---\n'+title+'\n\n')
        allquestion = re.sub("^(\s*)\[(.*?)\]","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        title = None

    # the id  : search the id (and remove it from the question)
    theid = re.search('(?<=\\\\qid\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theid:
        myid = theid.group(0)
        #print('\n\n---id---\n'+myid+'\n\n')
        allquestion = re.sub("\\\\qid\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        myid = None

    # the author : idem
    theauthor = re.search('(?<=\\\\qauthor\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theauthor:
        author = theauthor.group(0)
        #print('\n\n---auteur---\n'+author+'\n\n')
        allquestion = re.sub("\\\\qauthor\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        author = None

    # the classification : idem
    theclassification = re.search('(?<=\\\\qclassification\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theclassification:
        classification = theclassification.group(0)
        #print('\n\n---classification---\n'+classification+'\n\n')
        allquestion = re.sub("\\\\qclassification\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        classification = None

    # the tags : idem
    thetags = re.search('(?<=\\\\qtags\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if thetags:
        tags = thetags.group(0)
        #print('\n\n---tags---\n'+tags+'\n\n')
        allquestion = re.sub("\\\\qtags\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        tags = None

    # the type : idem
    thetype = re.search('(?<=\\\\qtype\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if thetype:
        mytype = thetype.group(0)
        #print('\n\n---type---\n'+mytype+'\n\n')
        allquestion = re.sub("\\\\qtype\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        mytype = None


    # the oneline flag : idem
    theoneline = re.search('\\\\qoneline',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theoneline:
        oneline = True       
        allquestion = re.sub("\\\\qoneline","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        oneline = False


    # the keeporder flag : idem
    thekeeporder = re.search('\\\\qkeeporder',allquestion, flags=re.MULTILINE|re.DOTALL)
    if thekeeporder:
        keeporder = True        
        allquestion = re.sub("\\\\qkeeporder","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        keeporder = False

    # the idontknow flag : idem
    theidontknow = re.search('\\\\qidontknow',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theidontknow:
        idontknow = True        
        allquestion = re.sub("\\\\qidontknow","",allquestion, flags=re.MULTILINE|re.DOTALL)
    else:
        idontknow = False

    # the image without options : idem
    image = None
    imageoptions = None
    theimage = re.search('(?<=\\\\qimage\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theimage:
        image = theimage.group(0)
        #print('\n\n---auteur---\n'+author+'\n\n')
        allquestion = re.sub("\\\\qimage\{(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)

    # the image with options : idem
    theimage = re.search('(?<=\\\\qimage\[)(.*?)(?=\]\{)(.*?)(?=\})',allquestion, flags=re.MULTILINE|re.DOTALL)
    if theimage:
        image = theimage.group(2)[2:]
        imageoptions = theimage.group(1)
        #print('\n\n---image ---\n'+image+'\n\n')
        #print('\n\n---image options---\n'+imageoptions+'\n\n')
        allquestion = re.sub("\\\\qimage\[(.*?)\}","",allquestion, flags=re.MULTILINE|re.DOTALL)


    #print('\n\n---New question---\n'+allquestion+'\n\n')       


    #only the question
    question = allquestion
    
    # Find the answers
    theanswers = re.search('(?<=\\\\begin{answers})(.*)(?=[\s*]\\\\end{answers})',text_exo, flags=re.MULTILINE|re.DOTALL)
    answers = theanswers.group(0)
    answers = answers.lstrip()
    #print('\n\n'+answers+'\n\n')


    eachanswer = re.split('\\\\(bad|good)',answers, flags=re.MULTILINE|re.DOTALL)

    #print(eachanswer)

    n = len(eachanswer)
    i = 1
    listans = []
    while i < n:
        theans = eachanswer[i+1]
        theans = re.sub("\s+\Z","",theans, flags=re.MULTILINE|re.DOTALL)
        ans = re.search('(?<=\{)(.*)(?=\})',theans, flags=re.MULTILINE|re.DOTALL).group(0)
        #print(' --- '+ans+'\n')
        if eachanswer[i]=='good':
            listans = listans + [{'correct':'True','value':ans}]
        else: 
            listans = listans + [{'correct':'False','value':ans}]
        i = i+2

    # Find the explanations
    theexplanations = re.search('(?<=\\\\begin{explanations})(.*)(?=[\s*]\\\\end{explanations})',text_exo, flags=re.MULTILINE|re.DOTALL)
    if theexplanations:
        explanations = theexplanations.group(0)
        explanations = explanations.lstrip()
        #print('\n\n'+explanations+'\n\n')
    else:
        explanations = None

    # Output of one exo
    text_yaml = ''
    text_yaml += '---\n'
    #text_yaml += "id: "+str(id)+'\n\n'

    if myid:
        text_yaml += "id: "+myid+'\n\n'

    if title:
        text_yaml += "title: "+title+'\n\n'

    if author:
        text_yaml += "author: "+author+'\n\n'

    if classification:
        text_yaml += "classification: "+classification+'\n\n'

    if tags:
        text_yaml += "tags: "+tags+'\n\n'

    if mytype:
        text_yaml += "type: "+mytype+'\n\n'

    if oneline:
        text_yaml += "oneline: True"+'\n\n'

    if keeporder:
        text_yaml += "keeporder: True"+'\n\n'

    if idontknow:
        text_yaml += "idontknow: True"+'\n\n'

    if image:
        text_yaml += "image: "+'\n'
        text_yaml += "    - file: "+image+'\n'
    if imageoptions:
        text_yaml += "      options: "+imageoptions+'\n\n'
    else:
        text_yaml += '\n'

    text_yaml += "question: |\n"+add_space(question)+'\n\n'
    text_yaml += "answers: \n"
    for ans in listans:
        text_yaml += "    - value: |\n"+add_space(ans['value'])+'\n'
        text_yaml += "      correct: "+ans['correct']+'\n\n'

    if explanations:
        text_yaml += "explanations: |\n"+add_space(explanations)+'\n\n'

    return text_yaml



#--------------------------------------------------
#--------------------------------------------------
# Split into each exercices
text_all_exo = re.findall('\\\\begin\{question\}(.*?)\\\\end\{question\}',text_all, flags=re.MULTILINE|re.DOTALL)

#print(text_all_exo)

#print('\n')
#print('text_all_exo[0])
#print('\n')
#print(text_all_exo[1])

#--------------------------------------------------
# Split into each exercices
with open(yaml_file, 'w', encoding='utf-8') as out:
    for text_exo in text_all_exo:
        text_yaml = one_exo_to_yaml(text_exo)
        out.write(text_yaml)






