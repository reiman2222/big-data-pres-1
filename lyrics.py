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



#Define gensim object
class TheCorpus(object):
    def __init__(self, path):
        #print('path in init: ' + path)
        self.pathToFile = path
    
    #returns list of tokens in lowercase split on whitespace with punctuation removed, lemmatized
    @staticmethod
    def tokenizeDocMedium(doc):
        docT = []
        wordnet_lemmatizer = WordNetLemmatizer()
        punctuationStripper = re.compile('[^\w-]+')
        
        for word in doc.split():
            w = punctuationStripper.sub('', word)
            w = wordnet_lemmatizer.lemmatize(w)
            if(w != ''):
                docT.append(w)

        return docT
    

 

    #def __iter__(self):
        



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

'''
def constructDictionary(pathToStopWordList):
    #print('statrting to make dict')
    tokenizedCorpus = []
    
    dictionary = corpora.Dictionary()
    numberRemover = re.compile("\d")

    #read stop list, convert to set for faster stop word removal
    stoplist = getStopWordList(pathToStopWordList)
    stopSet = set(stoplist)

    i = 1
    for fn in os.listdir('source'):
        with open('source' + '/' + fn, 'r', errors='ignore') as f:
            print(fn)
            doc = f.read()    
            if(i < articlesToProcess):
                if(doc):
                    #if(i < articlesToProcess):  
                    #TOKENIZE
                    docT = indexingUni(doc)
                    docTokenized = []
                    for t in docT:
                        if((t not in stopSet) and numberRemover.search(t) == None):
                            #print(t)
                            docTokenized.append(t)
                    
                    #print(docTokenized)
                    
                    tokenizedCorpus.append(docTokenized)
                    if(i % 100000 == 0):
                        print('compactifying dictionary every 100,000 documents to save memory')
                        dictionary.compactify()
                    if(i % 10000 == 0):
                        print('Another 10000 files processed, files added to dictionary')
                        dictionary.add_documents(tokenizedCorpus)
                        tokenizedCorpus = []

                else:
                    print('file had no content')
            else:
                break
            i += 1
        
    if(len(tokenizedCorpus) > 0):
        print('docs added')
        dictionary.add_documents(tokenizedCorpus)
    dictionary.compactify()
    return dictionary
'''            

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
            #print('true')

print('null lyrics: ' + str(numNullLyrics))
print('total songs: ' + str(len(listOfLyrics)))

tokenizedLyrics = []
for l in listOfLyrics:
	tokenizedLyrics.append(tokenize(l))

print(tokenizedLyrics[0])
print(listOfLyrics[0])        	    


dictionary = corpora.Dictionary(tokenizedLyrics)
print('dictionary size before prune: ' + str(len(dictionary)))
dictionary.filter_extremes(no_below=0, no_above=0.75)
print('dictionary size after prune: ' + str(len(dictionary)))





#dictionary = constructDictionary('stopwords.txt')


    
    
    
#pprint(len(dictionary.token2id))



#creates a corpus object for gensim
#theCorpus = TheCorpus('source')

#build tfidf model of theCorpus
#tfidf = models.TfidfModel(theCorpus)

#convert corpus from bag of words to tfidf vectors
#corpus_tfidf = tfidf[theCorpus]


