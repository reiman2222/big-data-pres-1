import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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
    nameInLyrics = []

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
            nameInLyrics.append('')
        else:
            listOfLyrics.append(currLyrics)
            if(row['Song'] in currLyrics):
                nameInLyrics.append('True')
            else:
                nameInLyrics.append('False')


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
#(unpruned lyrical complexity, pruned lyrical complexity, total words, posSent, negSent, compoundSent, repetitiveness)
lyricsStats = []
sid = SentimentIntensityAnalyzer()
for songL in tokenizedLyrics:
    if(songL[0] == 'None'):
        lyricsStats.append((-1,-1,-1, 0, 0, 0, -1))
    else:
        ss = sid.polarity_scores(' '.join(songL))
        unpruned = len(dictionary.doc2bow(songL))
        pruned = len(dictionaryPruned.doc2bow(songL))
        total = len(songL)
        rep = round(1.0 - (unpruned / (total + 0.0)), 3) #the higher the more repetitive
        lyricsStats.append((unpruned, pruned, total, ss['pos'], ss['neg'], ss['compound'], rep))



#write to new CSV
with open('billboard_lyrics_1964-2015.csv', 'r') as csvFile:
    reader = csv.DictReader(csvFile)
    
    with open('billboardLC.csv', 'w') as csvOut:
        fieldnames = ['Rank', 'Song', 'Artist', 'Year', 'UnprunedLyricalComplexity', 'TotalWords','TitleInLyrics',
            'posSent','negSent','compoundSent', 'repetitiveness']
        writer = csv.DictWriter(csvOut, fieldnames, restval='', extrasaction='raise', dialect='excel')    
        i = 0
        writer.writeheader()
        for row in reader:
            if(lyricsStats[i][0] == -1):
                writer.writerow({'Rank':row['Rank'], 'Song':row['Song'], 'Artist':row['Artist'], 'Year':row['Year'],
                    'UnprunedLyricalComplexity':'', 'TotalWords':'', 'TitleInLyrics':nameInLyrics[i], 'posSent': '',
                    'negSent': '', 'compoundSent': '', 'repetitiveness': ''})
            else:
                writer.writerow({'Rank':row['Rank'], 'Song':row['Song'], 'Artist':row['Artist'], 'Year':row['Year'],
                    'UnprunedLyricalComplexity':lyricsStats[i][0], 'TotalWords':lyricsStats[i][2], 
                    'TitleInLyrics':nameInLyrics[i],  'posSent': lyricsStats[i][3], 'negSent': lyricsStats[i][4],
                    'compoundSent': lyricsStats[i][5], 'repetitiveness': lyricsStats[i][6]})
            i += 1

print('Done')

