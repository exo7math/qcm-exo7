#!/usr/bin/env python3
"""
    Convertit un fichier moodle.xml en yaml
"""


import xml.etree.ElementTree as ET
import os
import re
import base64
from PIL import Image
from io import BytesIO
import argparse




parser = argparse.ArgumentParser(description='Conversion of moodle xml file to yaml file')

parser.add_argument('inputfile', help='input moodle xml filename')
parser.add_argument('outputfile', nargs='?', help='output yaml filename')

options = parser.parse_args()


moodle_file = options.inputfile
output = options.outputfile


stream = open(moodle_file, 'r', encoding='utf-8')
# Get argument : a tex file
file_name, file_extension = os.path.splitext(moodle_file) 

# Output file name 
if output:
    yaml_file = output    # Name given by user
else:
    yaml_file = file_name+'.yaml' # If no name add a .yaml extension








currentsections=""



image=re.compile("(<img.*@@PLUGINFILE@@/(.*png).*/>)")


tree = ET.parse(stream)
root=tree.getroot()


def images(str):
    """
        remplace la balise html <img> </img> par du code latex
        Attention le code ne fonctionne pas lorsqu'il y a deux images à remplacer
    """
    match = image.search(str)
    
    
    if match is not None:
       str=str.replace(match.groups()[0],"\includegraphics[width=8cm]{images/%s}"%(match.groups()[1]))
    return(str)
    
def removep(str):
    """
        Nettoie le texte en vue d'une utilisation de LaTeX
    """
    s=str
  
    replacements=[["&amp;","&"],["<p>",""],["</p>",""],["\]$$","$"],["\n"," "],["<P>",""],["</P>",""],["$$[","$"],["]$$","$"],["&nbsp;",""],["&rsquo;","'"],["&lt;","<"],["&gt;",">"],["$$","$"],["\(","$"],["\)","$"],["<br />",""],["%","~\%"]]
    for replacement in replacements:
        s=s.replace(replacement[0],replacement[1])
    s=images(s)
    
    return(s.strip())


def cleansectionname(str):
    """
        Les sections ne peuvent pas comporter le signe :
    """
    return str.replace(":",".")

def category(element):
    """
        traitement des noeux category, conversion en section et sous section
    """
    sout=""
    for el in element.iter('text'):
            s=el.text
    
    cats=s.split('/')
    if len(cats)>2:
            sout +="section: "+cleansectionname(cats[-2])+"\n"
    sout +="subsection: "+cleansectionname(cats[-1])+"\n"
           
    return(sout)

def reponse(out,answers):
    """ 
        Écrit un snippet yaml contenant les réponses 
    """
   
    print("answers:",file=out)
    for answer in answers:
        print("    - value: |\n        %s\n      correct: %s"%(answer[0],answer[1]),file=out)
        if answer[2] != "":
            print("      feedback: |\n%s\n"%answer[2],file=out)

def explanations(out,element):
    """
        Écrit la correction
    """
    if element != "":
        print("explanations: |\n%s\n"%(element),file=out)



        
def question(out,element):
    """
        Traitement d'une question:
            * insère les sections courrantes
            * quelques paramètres
            * enregistre les images
            * l'énoncé
            * les réponses
    """
    print("---\n",file=out)
    print(currentsections,file=out)
    if element.find('shuffleanswers').text=="true":
        print("keeporder: True\n",file=out)
    enonce=element.find('questiontext')[0].text
    print("question: |\n        "+removep(enonce)+"\n",file=out)
    #Les fichiers attachés
   
    for file in element.iter('file'):
        if file.get('encoding')=="base64":
            im = Image.open(BytesIO(base64.b64decode(file.text)))
            im.save("images/"+file.get('name'), 'PNG')   
    
    
    #Les réponses
    answers=[]
    for answer in element.iter('answer'):
            if float(answer.get('fraction'))>0:
                val="True"
            else:
                val="False"
            answers.append([removep(answer[0].text),val,removep(answer.find('feedback').text)])
    reponse(out,answers)
    #Les explications
    expls=""
    expls += element.find('correctfeedback').text
    expls += element.find('partiallycorrectfeedback').text
    expls += element.find('incorrectfeedback').text
    
    explanations(out,expls.strip())
        
    
    
    
with open(yaml_file, 'w', encoding='utf-8') as out:
    for child in root:
        if child.attrib['type']=='category':
            currentsections=category(child)
        if child.attrib['type']=='multichoice':
            question(out,child)
