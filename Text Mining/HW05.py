import os
os.chdir('C:/Users/Ritwik/OneDrive/BZAN557')  ## Set Working Directory accordingly 

import xml.etree.ElementTree as et 
xtree = et.parse("Pubmed.xml")
xroot = xtree.getroot()

bl_nodes = xtree.findall("PubmedArticle")
for node in bl_nodes:

    PMID = node.findtext('MedlineCitation/PMID')
    PubDate = ""
    for date in node.findall('MedlineCitation/Article/Journal/JournalIssue/PubDate/'):
        PubDate += (" " + date.text)
    
    Journal_title = node.findtext('MedlineCitation/Article/Journal/Title') 
    Article_title = node.findtext('MedlineCitation/Article/ArticleTitle') 
    Authors_list = node.findall('MedlineCitation/Article/AuthorList/Author') 
    Authors = []
    for author in Authors_list:
        Forename = author.find('ForeName').text if author.find('ForeName') is not None else ""
        Initials = author.find('Initials').text if author.find('Initials') is not None else ""
        Lastname = author.find('LastName').text if author.find('LastName') is not None else ""
        Authors.append(Forename + " " + Initials + " " + Lastname) 
        
    Abstract = ""
    for text in node.findall('MedlineCitation/Article/Abstract/AbstractText'):
        if text is None:
            Abstract = ""
        else:
            Abstract += text.text
    
df_cols = ["PMID", "Publication_Date", "Journal_Title", "Article_Title", "Authors", "Abstract"]
rows = []

rows.append({"PMID": PMID, "Publication_Date": PubDate, 
                 "Journal_Title": Journal_title, "ArticleTitle": Article_Title,
                 "Author": Authors, "Abstract": Abstract})

import pandas as pd
out_df = pd.DataFrame(rows, columns = df_cols)
print(out_df)    

#########################################################################################################################
from xml.etree import ElementTree

with open('Pubmed.xml', 'rt') as f:
    tree = ElementTree.parse(f)
 
for node in tree.iter():
    print (node.tag, node.text)

