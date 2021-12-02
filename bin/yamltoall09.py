#!/usr/bin/env python3

# Convert a yaml file to LaTeX file
# Usage : 'python yamltoall.py toto.yaml'
# Output : create a file toto.tex
# Other format 'python yamltoall.py -f amc toto.yaml' to convert it to 'amc' format
# Other format 'python yamltoall.py -f moodle toto.yaml' to convert it to 'moodle' format
# Other format 'python yamltoall.py -f latexmoodle toto.yaml' to convert it to 'latex' using 'moodle' package


import argparse
import yaml
import sys
import os
import string
import random
import re
import html
import base64


# Warning : answer['correct'] now appears to be a string 'True' or 'False' when imported from yaml file
# and no more a Boolean True/False (change has been made)


#--------------------------------------------------
#--------------------------------------------------
# Arguments 

parser = argparse.ArgumentParser(description='Conversion of mutliple choice questions from yaml to other format (LaTeX by default).')
parser.add_argument('-f', '--format', nargs='?', default='tex', help='output format file')
parser.add_argument('inputfile', help='input yaml filename')
parser.add_argument('outputfile', nargs='?', help='output filename')

options = parser.parse_args()

#print(options.inputfile)
#print(options.outputfile)
#print(options.format)

yaml_file = options.inputfile
output = options.outputfile
output_format = options.format


# OLD Get argument : a yaml file
#yaml_file = sys.argv[1]

 
#--------------------------------------------------
#--------------------------------------------------
# Input file / output file

# Input file name
file_name, file_extension = os.path.splitext(yaml_file) 

# Output file name 
if output:
    output_file = output    # Name given by user
else:
    if output_format == 'tex':
        output_file = file_name+'.tex' # Convert to .tex extension
    if output_format == 'amc':
        output_file = file_name+'.amc' # Convert to .amc extension
    if output_format == 'latexmoodle':
        output_file = file_name+'-moodle.tex' # Convert to latex with externam package 'moodle'        
    if output_format == 'moodle':  
        output_file =  file_name+'.xml' # Convert to a xml file with a.moodle extension (avec a.xml pour Moodle de ULille)
    if output_format == 'f2s':
        output_file =  file_name # Convert to a xml file with a quiz extension, but inside the "file_name" directory !

# Read all data
stream = open(yaml_file, 'r', encoding='utf-8')
my_data = yaml.load_all(stream,  Loader=yaml.BaseLoader)
all_data = list(my_data)
stream.close()


#--------------------------------------------------
#--------------------------------------------------
# Screen output
#for data in all_data:
#    print(data['question'])
#    for answers in data['answers']:
#        print(answers['value'])
#        correct = answers['correct']
#        if correct == True:
#             print("It's true\n")
#        else:    
#             print("It's false\n")  

def split_section(title):
    """ From a title like 'section | facile | 123.0' to a list of words (without code nb)
     :param title: 
    
    """
    title_split = title.split('|')
    title_split_bis = []
    for t in title_split:
        tt = re.sub(r'[,\\.\s]','',t,flags=re.MULTILINE)
        if not tt.isdigit():
            ttt = re.sub(r'^[\s]*','',t,flags=re.MULTILINE) # Delete potential space at the begin
            ttt = re.sub(r'[\s]*$','',ttt,flags=re.MULTILINE) # Delete potential space at the end
            title_split_bis.append(ttt)
    return title_split_bis

# Test
# print(split_section('Section, Section | Facile | 123.0, 123.5'))

 
#--------------------------------------------------
#--------------------------------------------------
#                   TEX
# Write data to a LaTeX file in our standardized format 
if output_format == 'tex':
  with open(output_file, 'w', encoding='utf-8') as out:
    for data in all_data:
        if 'title' in data.keys():
            out.write('\n\n\\begin{question}['+data['title']+']\n')
        else:
            out.write('\n\n\\begin{question}\n')

        if 'id' in data.keys():
            out.write('\\qid{'+str(data['id'])+'}\n')

        if 'author' in data.keys():
            out.write('\\qauthor{'+data['author']+'}\n')

        if 'classification' in data.keys():
            out.write('\\qclassification{'+data['classification']+'}\n')

        if 'tags' in data.keys():
            thetags = ""
            for tagdic in data['tags']:
                listtag = [(k,v) for k,v in tagdic.items()]

                tagkeywd, tagval = listtag[0]
                if type(tagval) == int or type(tagval) == float:
                    tagval = str(tagval)

                thetags += tagkeywd + "=" + tagval + ", "

            thetags = thetags[0:-2]  # supprime la dernière virgule en trop
            out.write('\\qtags{'+thetags+'}\n')

        if 'type' in data.keys():
            out.write('\\qtype{'+data['type']+'}\n')

        if 'tolerance' in data.keys():
            out.write('\\qtolerance{'+str(data['tolerance'])+'}\n')            

        if 'keeporder' in data.keys():
            if data['keeporder']:
                out.write('\\qkeeporder\n')

        if 'oneline' in data.keys():
            if data['oneline']:
                out.write('\\qoneline\n')

        if 'idontknow' in data.keys():
            if data['idontknow']:
                out.write('\\qidontknow\n')


        out.write('\n'+data['question']+'\n')

        # if 'image' in data.keys():
        #     dataimage = data['image'][0] 
        #     #print(dataimage)
        #     if 'options' in dataimage.keys():
        #         out.write('\\qimage['+dataimage['options']+']{'+dataimage['file']+'}\n\n')
        #     else:
        #         out.write('\\qimage{'+dataimage['file']+'}\n\n')     


        out.write('\\begin{answers}\n')    

        for answer in data['answers']:
            value = answer['value']
            value = value.rstrip()  #re.sub('[\s]*$','',text,flags=re.MULTILINE) # Delete potential space at the end
            correct = answer['correct']

            if 'feedback' in answer:
                feedback = answer['feedback']
                feedback = feedback.rstrip()
                value = value + '\n    \\feedback{' + feedback + '}\n    '

            if 'score' in answer:
                score = answer['score']
                score = str(score)
                value = value + '\\score{' + score + '}\n    '

            if correct == True:
                out.write('    \\good{'+value+'}\n')
            else:    
                out.write('    \\bad{'+value+'}\n')

     
        out.write('\\end{answers}\n') 

        if 'explanations' in data.keys():
            out.write('\\begin{explanations}\n'+data['explanations']+'\\end{explanations}\n')

        out.write('\\end{question}\n')


#--------------------------------------------------
#--------------------------------------------------
def replace_special_character(text):
    """
        Replace special character non well-suported in input file by Latex Moodle package
        :param text:
    """    

    # Replace 'ç' by '\c{c} ...
    text = re.sub(r"ç",r"\\c{c}",text, flags=re.MULTILINE|re.DOTALL)

    return text
 
#--------------------------------------------------
#--------------------------------------------------
#                   LATEXMOODLE
# Write data to a LaTeX file in our standardized format 
if output_format == 'latexmoodle':
  with open(output_file, 'w', encoding='utf-8') as out:
    for data in all_data:
        out.write('\n\n\\begin{multi}')

        # Options
        myoptions = ''
        myoptions += 'multiple,'   # multiple correct answers
        # Feedback: 
        if 'explanations' in data.keys():
            myoptions += 'feedback=\n{'+replace_special_character(data['explanations'])+'}'
        out.write('[' + myoptions + ']')  
        # Title (mandatory)    
        if 'title' in data.keys():
            out.write('{'+replace_special_character(data['title'])+'}\n')
        else:
            out.write('{Question}\n')

        # Question
        out.write(replace_special_character(data['question'])+'\n')

        # Answers
        for answer in data['answers']:
            value = replace_special_character(answer['value'])
            value = value.rstrip()  #re.sub('[\s]*$','',text,flags=re.MULTILINE) # Delete potential space at the end
            correct = answer['correct']
            if correct == 'True':
                out.write('    \\item* ' + value +'\n')
            else:    
                out.write('    \\item ' + value +'\n')

        out.write('\\end{multi}\n')


#--------------------------------------------------
#--------------------------------------------------

def replace_latex_macros(text):
    """
        Replace custom LaTeX macro for non-LaTeX export
        :param text:
    """
    
    # Replace \Rr to \mathbf{R} ...
    text = re.sub(r"\\Nn(?=[^a-zA-Z])",r"\\mathbf{N}",text, flags=re.MULTILINE|re.DOTALL)
    text = re.sub(r"\\Zz(?=[^a-zA-Z])",r"\\mathbf{Z}",text, flags=re.MULTILINE|re.DOTALL)
    text = re.sub(r"\\Qq(?=[^a-zA-Z])",r"\\mathbf{Q}",text, flags=re.MULTILINE|re.DOTALL)
    text = re.sub(r"\\Rr(?=[^a-zA-Z])",r"\\mathbf{R}",text, flags=re.MULTILINE|re.DOTALL)
    text = re.sub(r"\\Cc(?=[^a-zA-Z])",r"\\mathbf{C}",text, flags=re.MULTILINE|re.DOTALL)
    text = re.sub(r"\\Kk(?=[^a-zA-Z])",r"\\mathbf{K}",text, flags=re.MULTILINE|re.DOTALL)

    text = re.sub(r"\\pgcd",r"\\text{pgcd}",text, flags=re.MULTILINE|re.DOTALL)   
    text = re.sub(r"\\ppcm",r"\\text{ppcm}",text, flags=re.MULTILINE|re.DOTALL)   
    text = re.sub(r"\\Card",r"\\text{Card}",text, flags=re.MULTILINE|re.DOTALL)   
    text = re.sub(r"\\val(?=[^a-zA-Z])",r"\\text{val}",text, flags=re.MULTILINE|re.DOTALL)


    # Replace '<' (resp. '>'') by ' < ' (resp. ' > ') to avoid html mixed up (note the spaces)
    # text = re.sub("<"," < ",text, flags=re.MULTILINE|re.DOTALL)
    # text = re.sub(">"," > ",text, flags=re.MULTILINE|re.DOTALL)

    # text = re.sub("\((.*?)<(.*?)\)","(\g<1> < \g<2>)",text, flags=re.MULTILINE|re.DOTALL)
    # text1 = re.sub("\$(.+?)\$","\\\(\g<1>\\\)",text2, flags=re.MULTILINE|re.DOTALL)

    # Gestion of "<"" in text mode (do nothing) and math mode (add space)
    # Would be happy to have a solution using regex!!!
    in_math = False
    is_slash = False
    new_text = ""
    for c in text:
        if is_slash and (c == "(" or c == "["):
            in_math = True
        if is_slash and (c == ")" or c == "]"):
            in_math = False
        if c == "\\":
            is_slash = True
        else:
            is_slash = False
        if in_math and (c == "<" or c == ">"):
            new_text += " " + c + " "
        else:
            new_text += c
    text = new_text

    return text

# Test
# text = "Une question avec une balise html <a>lien</a>. Et ici des maths \(b<a\) et \(a<b<c>b>a\), ici (a<b<c) la une formule :\[a<b<i>a'\]"
# print(text)
# text = replace_latex_macros(text)
# print(text)

def delete_exo7_category(text):
    
    """Delete the code from the section title
    Example "My Section | Easy | 123.45" -> "My Section | Easy"
    :param text: texte
    """
    
    text = re.sub(r"\s\|\s[0-9.,\s]+","",text, flags=re.MULTILINE|re.DOTALL)

    return text

# Test
# text = "Logique | Facile | 100.01, 100.02"
# print(text)
# text = delete_exo7_category(text)
# print(text)

# text = "Logique -- Raisonnement | 100"
# print(text)
# text = delete_exo7_category(text)
# print(text)



#--------------------------------------------------
#--------------------------------------------------

def id_generator(size=6, chars=string.ascii_lowercase):
    """Random word generator (from stackoverflow)
    :param size: longueur de l'identifiant (Default value = 6)
    :param chars: alphabet (Default value = string.ascii_lowercase)
    """
    return ''.join(random.choice(chars) for _ in range(size))

#--------------------------------------------------
#--------------------------------------------------
#                      AMC
# Write data to a LaTeX file in the format 'amc'
if output_format == 'amc':
  with open(output_file, 'w', encoding='utf-8') as out:
    for data in all_data:
        
        if 'id' in data.keys():
            myid = str(data['id'])
        else:
            myid = id_generator()
        if 'subsection' in data.keys():
            out.write('\\element{'+data['subsection']+'}{')
        if 'type' in data.keys() and ( data['type'] == 'onlyone'  or data['type'] == 'truefalse' ):
            out.write('\n\n\\begin{question}{'+myid+'}\n\n')
        else:
            out.write('\n\n\\begin{questionmult}{'+myid+'}\n\n')

        if 'author' in data.keys():
            out.write('%Author: '+data['author']+'\n\n')

        if 'classification' in data.keys():
            out.write('%Classification: '+data['classification']+'\n\n')

        # if 'tags' in data.keys():
        #     out.write('%\\tags{'+data['tags']+'.}\n\n')

        if 'title' in data.keys():
            thetitle = replace_latex_macros(data['title'])
            out.write('\\textbf{'+ thetitle +'.} ')

        thequestion = replace_latex_macros(data['question'])
        thequestion = re.sub(r"\\qimage",r"\\includegraphics",thequestion, flags=re.MULTILINE|re.DOTALL)
        out.write(thequestion+'\n')



        # if 'image' in data.keys():
        #     dataimage = data['image'][0] 
        #     out.write('\\begin{center}\n')
        #     if 'options' in dataimage.keys():
        #         out.write('\\includegraphics['+dataimage['options']+']{'+dataimage['file']+'}')
        #     else:
        #         out.write('\\includegraphics{'+dataimage['file']+'}')     
        #     out.write('\n\\end{center}\n\n')

        if 'oneline' in data.keys() and data['oneline']:
            out.write('\\begin{choiceshoriz}')
        else:
            out.write('\\begin{choices}')

        if 'keeporder' in data.keys() and data['keeporder']:
            out.write('[o]\n')
        else:
            out.write('\n')  

        for answers in data['answers']:
            value = answers['value']
            value = replace_latex_macros(value.rstrip())  #re.sub('[\s]*$','',text,flags=re.MULTILINE) # Delete potential space at the end
            value = re.sub(r"\\qimage",r"\\includegraphics",value, flags=re.MULTILINE|re.DOTALL)

            correct = answers['correct']

            if correct == 'True':
                out.write('    \\correctchoice{'+value+'}\n')
            else:    
                out.write('    \\wrongchoice{'+value+'}\n')

        if 'oneline' in data.keys() and data['oneline']:
            out.write('\\end{choiceshoriz}\n')
        else:
            out.write('\\end{choices}\n')     

        if 'explanations' in data.keys():
            theexplanations = replace_latex_macros(data['explanations'].rstrip())
            theexplanations = re.sub(r"\\qimage",r"\\includegraphics",theexplanations, flags=re.MULTILINE|re.DOTALL)

            out.write('\\explain{'+ theexplanations +'}\n')

        if 'type' in data.keys() and ( data['type'] == 'onlyone'  or data['type'] == 'truefalse' ):
            out.write('\\end{question}\n')
        else:
            out.write('\\end{questionmult}\n')
        if 'subsection' in data.keys():
            out.write('}\n\n')
 
#--------------------------------------------------
#--------------------------------------------------
#                   MOODLE
# Write data to a xml file in a moodle format

# nom du cours
COURSE_NAME_TEXT = 'Qcm Exo7/'
# préfixe pour les noms de questions dans l'export Moodle
THENUM_PREFIX = 'qcm-exo7-' 

def encode_image(filename):
    """Encode an image to be included in xml
   
    :param filename: nom de fichier image sans le .png
    
    """
    
    filename =  filename + '.png'
    with open(filename, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('ascii')
    data = '</p><p>\n<img style="max-width:100%; margin: 10px auto;" src="data:image/png;base64,'+encoded+'"/>\n'
    return data

def replace_images(data):
    
    """Replace all input of images by their encoding
    :param data: texte
    """

    # the image without options : idem
    theimage = re.search(r'\\qimage',data, flags=re.MULTILINE|re.DOTALL)

    while theimage is not None:
        # the image without options
        theimage = re.search(r'(?<=\\qimage\{)(.*?)(?=\})',data, flags=re.MULTILINE|re.DOTALL)
        if theimage:
            image_name = theimage.group(0)
            # print("sans option",image_name)
            new_image = encode_image(image_name)
            data = re.sub(r"\\qimage\{(.*?)\}",new_image,data, flags=re.MULTILINE|re.DOTALL)
        else:
        # the image with options
            theimage = re.search(r'(?<=\\qimage\[)(.*?)(?=\]\{)(.*?)(?=\})',data, flags=re.MULTILINE|re.DOTALL)
            image_name = theimage.group(2)[2:]
            image_options = theimage.group(1)
            # print("avec option",image_name,image_options)
            new_image = encode_image(image_name)
            data = re.sub(r"\\qimage\[(.*?)\]\{(.*?)\}",new_image,data, flags=re.MULTILINE|re.DOTALL)

        # Next image?
        theimage = re.search(r'\\qimage',data, flags=re.MULTILINE|re.DOTALL)

    return data

    



beginmoodle = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n'
endmoodle = '\n\n</quiz>\n'

if output_format == 'moodle':
  with open(output_file, 'w', encoding='utf-8') as out:

    out.write(beginmoodle)

    for data in all_data:

        if 'section' in data.keys():
            thesection = delete_exo7_category(data['section'])

            if 'subsection' in data.keys():           
                thesubsection = '/' + delete_exo7_category(data['subsection'])
            else:
                thesubsection = ''

            course_name = COURSE_NAME_TEXT

            out.write('\n\n<question type="category">\n<category>\n<text>\n$course$/'+course_name
                +thesection+thesubsection+'</text>\n</category>\n</question>\n\n')



#        if 'id' in data.keys():
#            myid = str(data['id'])
        single = False

        if 'type' in data.keys() and ( data['type'] == 'numerical' ):
            out.write('\n\n<question type="numerical">\n')
        elif 'type' in data.keys() and ( data['type'] == 'onlyone'  or data['type'] == 'truefalse' ):
            single = True
            out.write('\n\n<question type="multichoice">\n')
            out.write('<single>true</single>\n')
        else:
            out.write('\n\n<question type="multichoice">\n')
            out.write('<single>false</single>\n')


        if 'num' in data.keys():
            thenum = THENUM_PREFIX+str(data['num']).zfill(4)
            out.write('<name><text>'+ thenum +'</text></name>\n')
        else: 
            out.write('<name><text> </text></name>\n')

        # Tags pour export vers scenari
        # Tags automatiques depuis section, subsection,...
        autotags = ""
        existing_tags = []
        if 'tags' in data.keys():
            existing_tags = [list(t.keys())[0] for t in data['tags']]

        if 'author' in data.keys():
            tagkeywd,tagval = 'auteur',data['author']
            autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        if 'section' in data.keys():
            thesection = data['section']
        else:
        	thesection = ""

        if 'subsection' in data.keys():
            thesubsection = data['subsection']
        else:
        	thesubsection = ""

        # Complexité automatique depuis la section/sous-section 

        if 'complexite' not in existing_tags:  
            if ('Facile' in thesection) or ('Facile' in thesubsection):
                tagkeywd,tagval = 'complexite','2'
                autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

            if ('Moyen' in thesection) or ('Moyen' in thesubsection):
                tagkeywd,tagval = 'complexite','3'
                autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

            if ('Difficile' in thesection) or ('Difficile' in thesubsection):
                tagkeywd,tagval = 'complexite','4'
                autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        # Catégorie pour scenari

        tagval = ""
        if 'Logique' in thesection:
            tagval = 'Logique et raisonnements'
        elif 'Suites' in thesection:
            tagval = 'Suites'
        elif ('Continuité' in thesection) or ('Limite' in thesection) or  ('Ensembles' in thesection) or ('Fonctions' in thesection):
            tagval = 'Fonctions'
        elif  'Dérivabilité' in thesection:
            tagval = 'Dérivation'
        elif ('Nombres complexes' in thesection) or ('Réels' in thesection):
            tagval = 'Nombres réels et complexes'
        elif 'Polynômes' in thesection:
            tagval = 'Polynômes'  
        elif 'Géométrie' in thesection:
            tagval = 'Géométrie'      

        if ('theme' not in existing_tags) and (len(tagval)>0):
            tagkeywd = 'theme'
            autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        # Niveau
        if 'niveau' not in existing_tags:
            tagkeywd,tagval = 'niveau','L1'
            autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        # Titre et mots-clés
        if len(thesection)>0:
            mots_section = split_section(thesection)
        else:
            mots_section = []
        if len(thesubsection)>0:
            mots_subsection = split_section(thesubsection)
        else:
            mots_subsection = []

        titre = " - ".join(mots_section+mots_subsection)
        mots_cles = ", ".join(mots_section+mots_subsection)
        # print(mots_cles)
        if 'titre' not in data.keys():
            tagkeywd,tagval = 'titre',titre
            autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'
        
        # if 'motcle' not in existing_tags:   # Comment to enable both automatic and manual keywords    
        for mot in mots_section+mots_subsection:
            tagkeywd,tagval = 'motcle',mot
            autotags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        if 'link' in data.keys():
            thelink = data['link']
            # For tags
            for l in thelink:
                tagkeywd = 'lien'
                autotags += '    <tag><text>' + tagkeywd + "=" + l['link']+'['+l['type']+']['+l['title']+']'+'</text></tag>\n'
            # For explanations

            link_explanations = '\n Liens :\n'
            for l in thelink:
                link_explanations += '<a href="' + l['link'] + '">' + l['title'] + ' (' + l['type'] + ')</a> \n'

        # print(autotags)
        # Tags depuis la clé tags

        thetags = autotags
        if 'tags' in data.keys():
            for tagdic in data['tags']:
                listtag = [(k,v) for k,v in tagdic.items()]

                tagkeywd, tagval = listtag[0]
                if type(tagval) == int or type(tagval) == float:
                    tagval = str(tagval)

                thetags += '    <tag><text>' + tagkeywd + "=" + tagval + '</text></tag>\n'

        if len(thetags)>0:
            out.write('<tags>\n'+thetags+'</tags>\n')

        # question
        thequestion = replace_latex_macros(data['question'])
        thequestion = replace_images(thequestion)
        out.write('<questiontext format="html">\n')
        out.write('<text><![CDATA[<p>\n')
        out.write(thequestion)
        
        # #image in the question
        # if 'image' in data.keys():
        #     dataimage = data['image'][0]
        #     image_file =  dataimage['file']+'.png'
        #     with open(image_file, "rb") as image_file:
        #         encoded = base64.b64encode(image_file.read()).decode('ascii')
        #     #print(encoded)
        #     out.write('</p><p>\n<img src="data:image/png;base64,')            
        #     out.write(encoded)
        #     out.write('"/>\n')

        # end of the question
        out.write('<br></p>]]></text>\n')
        out.write('</questiontext>\n<defaultgrade>1.0</defaultgrade>\n')

        if 'explanations' in data.keys():
            theexplanations = replace_latex_macros(data['explanations'])
            theexplanations = replace_images(theexplanations)
            out.write('<generalfeedback format="html"><text><![CDATA[<p>\n')
            out.write(theexplanations)
            if 'link' in data.keys():
                out.write(link_explanations)   
            out.write('</p>]]></text></generalfeedback>\n')

        if 'type' in data.keys() and ( data['type'] == 'numerical' ):
            out.write('<penalty>0.33</penalty>\n')
            out.write('<hidden>0</hidden>\n')
        elif 'keeporder' in data.keys() and data['keeporder']:
            out.write('<shuffleanswers>0</shuffleanswers>\n')
            out.write('<answernumbering>abc</answernumbering>\n')
        else:
            out.write('<shuffleanswers>1</shuffleanswers>\n')
            out.write('<answernumbering>abc</answernumbering>\n')

        

        nbans = 0
        nbgood = 0
        nbbad = 0
        for answers in data['answers']:
            correct = answers['correct']
            nbans += 1
            if correct == 'True':
                nbgood += 1
            else:
                nbbad += 1
        
        if ('type' not in data.keys()) or ('type' in data.keys() and ( data['type'] != 'numerical' )):    
            if nbgood > 0:
                goodratio = str("%.5f" % float(100/nbgood))
            else: 
                goodratio = "0"
            if nbbad > 0: 
                badratio = str("%.5f" % float(100/nbbad))
            else:
                badratio = "0"

            for answer in data['answers']:
                if answer['correct'] == "True":
                    out.write('<answer fraction="'+goodratio+'" format="html"><text><![CDATA[<p>\n')
                else:
                    out.write('<answer fraction="0" format="html"><text><![CDATA[<p>\n')
                thevalue = replace_latex_macros(answer['value'])
                thevalue = replace_images(thevalue)

                out.write(thevalue)
                out.write('</p>]]></text>\n')

                if 'feedback' in answer:
                    feedback = replace_latex_macros(answer['feedback'])
                    feedback = replace_images(feedback)
                    feedback = feedback.rstrip()
                    out.write('<feedback><text><![CDATA[<p>' + feedback + '</p>]]></text></feedback>\n')
            
                out.write('</answer>\n')

        else:
            for answer in data['answers']:
                if answer['correct'] == 'True':
                    if 'score' in answer:
                        myscore = str("%.0f" % float(answer['score']))
                        out.write('<answer format="moodle_auto_format" fraction="' + myscore + '"><text><![CDATA[\n')
                    else:
                        out.write('<answer format="moodle_auto_format" fraction="100"><text><![CDATA[\n')
                else:
                    out.write('<answer format="moodle_auto_format" fraction="0"><text><![CDATA[\n')
                
                thevalue = replace_latex_macros(answer['value'])
                thevalue = replace_images(thevalue)

                out.write(thevalue)
                out.write(']]></text>\n')

                if 'feedback' in answer:
                    feedback = replace_latex_macros(answer['feedback'])
                    feedback = replace_images(feedback)
                    feedback = feedback.rstrip()
                    out.write('<feedback><text><![CDATA[<p>' + feedback + '</p>]]></text></feedback>\n')

                if 'tolerance' in data.keys():
                    mytolerance = str("%.5f" % float(data['tolerance']))
                    out.write('<tolerance>' + mytolerance + '</tolerance>\n')
                else:
                    out.write('<tolerance>0</tolerance>\n')
                    
                out.write('<unitgradingtype>0</unitgradingtype>\n')
                out.write('<unitpenalty>0.1</unitpenalty>\n')
                out.write('<showunits>3</showunits>\n')
                out.write('<unitsleft>0</unitsleft>\n')
                out.write('</answer>\n')
            


#            value = 
#            value = value.rstrip()  #re.sub('[\s]*$','',text,re.MULTILINE) # Delete potential space at the end
#            correct = 
#              correct == True:
#                out.write('    \\correctchoice{'+value+'}\n')
#            else:    
#                out.write('    \\wrongchoice{'+value+'}\n')
        if 'type' in data.keys() and ( data['type'] != 'numerical' ):  
            if single:
                out.write('<single>true</single>\n')  
            else:
                out.write('<single>false</single>\n')
    
            
            
        out.write('</question>')

    out.write(endmoodle)


#--------------------------------------------------
#--------------------------------------------------
#                 FAQ2SCIENCES (f2s)
#--------------------------------------------------

def f2sxmlcleanup(data):
    """Write data to a xml file in a Scenari / faq2sciences format
    :param data:
    """
    
    data = html.escape(data)
    data = re.sub(r'\$(.*?)\$', r'<sc:textLeaf role="mathtex">\1</sc:textLeaf>', data)
    data = re.sub(r'\\\[(.*?)\\\]', r'<sc:textLeaf role="mathtex">\1</sc:textLeaf>', data)
    data = re.sub(r'\\\((.*?)\\\)', r'<sc:textLeaf role="mathtex">\1</sc:textLeaf>', data)
    data = re.sub(r'\\textbf\{(.*?)\}', r'<sc:inlineStyle role="emp">\1</sc:inlineStyle>', data)
    return data

beginf2s = '<?xml version="1.0" encoding="UTF-8"?>\n<sc:item xmlns:sc="http://www.utc.fr/ics/scenari/v3/core">\n'
endf2s = '\n</sc:item>\n'

if output_format == 'f2s':
    os.mkdir(output_file)

    for data in all_data:
        if 'id' in data.keys():
            file_id = str(data['id'])
        else:
            file_id = id_generator()
        out = open(os.path.join(output_file, file_id+'.quiz'), 'w', encoding='utf-8')
        out.write(beginf2s)

        single = False

        if 'type' in data.keys() and ( data['type'] == 'onlyone'  or data['type'] == 'truefalse' ):
            single = True
            out.write('\n\n<op:mcqSur xmlns:op="utc.fr:ics/opale3" xmlns:sp="http://www.utc.fr/ics/scenari/v3/primitive">\n')
        else:
            out.write('\n\n<op:mcqMur xmlns:op="utc.fr:ics/opale3" xmlns:sp="http://www.utc.fr/ics/scenari/v3/primitive">\n')

        if 'title' in data.keys():
            thetitle = replace_latex_macros(data['title'])
            out.write('<op:exeM><sp:title>'+ thetitle +'</sp:title></op:exeM>\n')
        else: 
            out.write('<op:exeM></op:exeM>\n')

        thequestion = replace_latex_macros(data['question'])
        out.write('<sc:question><op:res><sp:txt><op:txt><sc:para xml:space="preserve">\n')
        out.write(f2sxmlcleanup(thequestion))
        out.write('</sc:para></op:txt></sp:txt></op:res></sc:question>\n')


#        if 'image' in data.keys():
#            dataimage = data['image'][0] 
#            out.write('\\begin{center}\n')
#            if 'options' in dataimage.keys():
#                out.write('\\includegraphics['+dataimage['options']+']{'+dataimage['file']+'}')
#            else:
#                out.write('\\includegraphics{'+dataimage['file']+'}')     
#            out.write('\n\\end{center}\n\n')

        good = 1
        out.write('<sc:choices>\n')
        for answer in data['answers']:

            checkstate = ''
            if not (single):
                if answer['correct'] == 'True':
                    checkstate = ' solution="checked"'
                else:
                    checkstate = ' solution="unchecked"'
            out.write('<sc:choice'+checkstate+'><sc:choiceLabel><op:txt><sc:para xml:space="preserve">\n')
            thevalue = replace_latex_macros(answer['value'])
            out.write(f2sxmlcleanup(thevalue))
            out.write('</sc:para></op:txt></sc:choiceLabel>')

            if 'feedback' in answer:
                feedback = replace_latex_macros(answer['feedback'])
                feedback = f2sxmlcleanup(feedback)
                feedback = feedback.rstrip()
                out.write('<sc:choiceExplanation><op:txt><sc:para xml:space="preserve">\n' + feedback +'</sc:para></op:txt></sc:choiceExplanation>\n')

            out.write('</sc:choice>\n')
            good+=1

        out.write('</sc:choices>')
        if single:
            out.write('<sc:solution choice="'+str(good)+'"/>')
        if 'explanations' in data.keys():
            theexplanations = replace_latex_macros(data['explanations'])
            out.write('<sc:globalExplanation><op:res><sp:txt><op:txt><sc:para xml:space="preserve">\n')
            out.write(f2sxmlcleanup(theexplanations))
            out.write('</sc:para></op:txt></sp:txt></op:res></sc:globalExplanation>\n')

        if single:
            out.write('\n\n</op:mcqSur>\n')
        else:
            out.write('\n\n</op:mcqMur>\n')

        out.write(endf2s)
