import nltk
#nltk.download("wordnet")
#nltk.download('stopwords')

#import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from smart_open import smart_open
import json
from gensim import corpora, models, similarities
import tempfile
from collections import defaultdict
from pprint import pprint #pretty printer

import string
import re

#getStopWordList(pathToSWL) returns a list of stopwords contained in file
#located at pathToSWL. 
#getStopWordList EXPECTS the stop words in the text file to be deliniated by whitespace
def getStopWordList(pathToSWL):
    #print('Reading stopword list from: ' + pathToSWL + '\n')

    f = open(pathToSWL, 'r')
    fcontents = f.read()
    stopWordList = fcontents.split()
    f.close()

    return stopWordList

          

#-----------------------------------------------------------------------------------------------------------------#

#----------------------------------#
#               Main               #
#----------------------------------#


def addLyricalComplexity(pathtoCSV):
    return 0

#returns list of tokens in lowercase split on whitespace with punctuation removed, lemmatized
def tokenize(doc):
    docT = []
    punctuationStripper = re.compile('[^\w-]+')
        
    for word in doc.split():
        w = punctuationStripper.sub('', word)
        if(w != ''):
            docT.append(w)

    return docT


#read csv file into memory
import csv
with open('billboard_lyrics_1964-2015.csv', 'r') as csvFile:
    reader = csv.DictReader(csvFile)
    
    listOfLyrics = []    
    
    numNullLyrics = 0

    for row in reader:
        currLyrics = row['Lyrics']
        #print(row['Lyrics'])
        #print('====================================================================')
        #numNullLyrics = 0

        currLyrics = currLyrics.strip()

        

        if(currLyrics == 'NA' or currLyrics == '' or currLyrics == None):
            listOfLyrics.append('None')
            numNullLyrics += 1
        else:
        	listOfLyrics.append(currLyrics)


print('null lyrics: ' + str(numNullLyrics))
print('total songs: ' + str(len(listOfLyrics)))

tokenizedLyrics = []
for l in listOfLyrics:
	tokenizedLyrics.append(tokenize(l))       	    


dictionary = corpora.Dictionary(tokenizedLyrics)
print('dictionary size before prune: ' + str(len(dictionary)))

dictionaryPruned = corpora.Dictionary(tokenizedLyrics)
dictionaryPruned.filter_extremes(no_below=0, no_above=0.5)
print('dictionary size after prune: ' + str(len(dictionaryPruned)))


#lyricsStats is a list of tuples of the form 
#(unpruned lyrical complexity, pruned lyrical complexity, total words)
lyricsStats = []
for songL in tokenizedLyrics:
    if(songL[0] == 'None'):
        lyricsStats.append((-1,-1,-1))
    else:
        lyricsStats.append((len((dictionary.doc2bow(songL))), len(dictionaryPruned.doc2bow(songL)), len(songL)))



#write to new CSV
with open('billboard_lyrics_1964-2015.csv', 'r') as csvFile:
    reader = csv.DictReader(csvFile)
    
    with open('billboardLC.csv', 'w') as csvOut:
        fieldnames = ['Rank', 'Song', 'Artist', 'Year', 'UnprunedLyricalComplexity', 'PrunedLyricalComplexity', 'TotalWords']
        writer = csv.DictWriter(csvOut, fieldnames, restval='', extrasaction='raise', dialect='excel')    
        i = 0
        writer.writeheader()
        for row in reader:
            if(lyricsStats[i] == (-1,-1,-1)):
                writer.writerow({'Rank':row['Rank'], 'Song':row['Song'], 'Artist':row['Artist'], 'Year':row['Year'],
                    'UnprunedLyricalComplexity':'', 'PrunedLyricalComplexity':'', 'TotalWords':''})
            else:
                writer.writerow({'Rank':row['Rank'], 'Song':row['Song'], 'Artist':row['Artist'], 'Year':row['Year'],
                    'UnprunedLyricalComplexity':lyricsStats[i][0], 'PrunedLyricalComplexity':lyricsStats[i][1], 'TotalWords':lyricsStats[i][2]})
            i += 1

print('Done')
