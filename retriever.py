import numpy as np
import re
from math import log2
from time import time
from nltk.stem import PorterStemmer as Stemmer
import sqlite3
from zlib import crc32
from pathlib import Path
from itertools import chain
from collections import Counter
import sqlite3
import os 

ALPHA = 0.8 #titles matching
BETA = 1 - ALPHA #text matching 
MAX_RESULTS = 50 # max results that can be returned

Title_globalPageDict = {}
Text_globalPageDict = {}

globalWordtoID = {}

Title_globalPageStemText = {}
Text_globalPageStemText = {}

allDocs = []

ps = Stemmer()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

stopword_path = str(Path.cwd().parent ) + 'stopwords.txt'
globalWordtoID = {}

with open( 'stopwords.txt', 'r') as file:
    stopwords = file.read().split()

connection = sqlite3.connect(db_path)  # Set check_same_thread to False because Flask initialized the connection in a different thread, this is safe because the search engine is read only
cursor = connection.cursor()

DOCUMENT_COUNT = cursor.execute(
    """
        SELECT COUNT(page_id) FROM web_info
    """).fetchone()[0] # total number of documents in the database

DOCUMENT_COUNT = float(DOCUMENT_COUNT)

def parse_string(query: str)->list[list[int]]:
    """
    `Input`: query: str: The string entered in the text box
    `Return`: Array of arrays, 
        `index 0`: is the encoding of the all words in the string
        `index 1`: is the encoding of the words which are phrases
    """

    resultArray = []
    # Create two arrays of phrases and words to be queried.
    start = time()
    single_word = []

    for idx,word in enumerate(query.split()):
        if (idx == 10000):
            break
        processedWord:str = re.sub("[^a-zA-Z-]+", "", word.lower())
        stemmedWord:str
        if (processedWord not in stopwords):
            stemmedWord = ps.stem(processedWord)
            try:
                single_word.append(globalWordtoID[stemmedWord])
            except:
                pass

    resultArray.append(single_word)
    end = time()
    print("time taken for query:", end - start)
    
    # Remove every stopwords in the single_word as they are not necessary.
    # During the process we will also stem the word
    phrases_no_stopword = []
    phrases = [x.lower() for x in re.findall('"([^"]*)"', query) if x]
    for phrase in phrases:
        querywords = phrase.split()

        resultwords = [ps.stem(word) for word in querywords if word.lower() not in stopwords]
        result = r"(?<!\S){}(?!\S)".format(" ".join(resultwords))

        phrases_no_stopword.append(result)

    resultArray.append(phrases_no_stopword)
    
    return resultArray


def documentToVec(page_id, fromTitle):  #need fix frequency in tables 
    vector = {}
    
    if page_id == None: 
        return vector
    
    inverted_table =  "title_inverted_index" if fromTitle else "inverted_idx"
        
    wordsList = cursor.execute(
        f"""
            SELECT keyword_id, frequency FROM {inverted_table} WHERE page_id = ?
        """, 
        (page_id,)).fetchall() 
        
    maxTF = cursor.execute(
        f"""
            SELECT MAX(frequency) FROM {inverted_table} WHERE page_id = ?                   
        """,
        (page_id,)).fetchone()[0]
    
    forwardIdx = "forward_idx"  if fromTitle else "title_forward_index"
        
    word_ids = [word for word, _ in wordsList]
    queryArray = ["?"] * len(word_ids)

    word_counts = cursor.execute(
        f"""
            SELECT keyword_id, frequency FROM {forwardIdx} WHERE keyword_id IN ({','.join(queryArray)})
        """, 
        word_ids).fetchall()
    
    Doc_count = {word_id: count for word_id, count in word_counts}
    
    for word, tf in wordsList:
        vector[word] = tf * log2(DOCUMENT_COUNT / Doc_count[word]) / maxTF
    
    return vector   

def queryToVec(queryEncode):
    
    if (len(queryEncode) == 0):
        return {}
    
    vector = {}
    wordsTF= Counter(queryEncode)
    
    for word,tf in list(wordsTF.items()):
        vector[word] = tf
    
    return vector

def cosineSimilarity(queryVec, docVec):
    """
        Input: 2 dictionariest of word and their frequency in the document.
        output: cosine distance of query Vector and Document vector 
    """
    
    if (len(queryVec) == 0 or len(docVec) == 0):
        return 0
    
    red_queryVec = {key: value for key, value in queryVec.items() if key in docVec}
    red_docVec = {key: value for key, value in docVec.items() if key in queryVec}
    
    dotProduct = sum(red_queryVec[word] * red_docVec[word] for word in red_queryVec)
    documentMagnitude = sum(value*value for value in docVec.values()) ** 0.5
    
    return dotProduct / documentMagnitude


def phraseFilter(doc_id, phases):
    """
    doc_id: The id of the document
    phases: The list of phrases to be queried
    
    `Return` True if the document contains all the phrases, False otherwise
    """
    if (len(phases) == 0 or len(phases[0]) == 0):
        return True

    docTitle = Title_globalPageStemText[doc_id]
    
    doctxt = Text_globalPageStemText[doc_id]

    for phrase in phases:
        if not re.search(phrase, docTitle) and not re.search(phrase, doctxt):
            return False    

    return True



def queryFilter(doc_id, query):
    """
    doc_id:  The id of the document
    query: The list of words to be queried
    
    `Return` True if the document contains any of the words, False otherwise
    """
    if (len(query) == 0):
        return True

    docTitle_list = list(Title_globalPageDict[doc_id].keys())
    doctxt_List = list(Text_globalPageDict[doc_id].keys())

    for word in query:
        if word in docTitle_list or word in doctxt_List:
            return True

    return False



def search_engine(query: str)->dict[int,float]:
    if (query == None or query == ""):
        return {}
    
    splitted_query = parse_string(query)

    if (len(splitted_query[0]) == 0): # incase query is something out of the db
        return {}
    
    queryVector = queryToVec(splitted_query[0])

    
    title_cosineScores = {}
    text_cosineScores = {}

    for document in allDocs:
        document = document[0]
        if (len(splitted_query[1]) > 0):
            if not phraseFilter(document,splitted_query[1]):
                continue
        else:
            if not queryFilter(document,splitted_query[0]):
                continue            
        
        title_documentVector = Title_globalPageDict[document]
        text_documentVector = Text_globalPageDict[document]
        
        title_similarity = cosineSimilarity(queryVector,title_documentVector)
        text_similarity = cosineSimilarity(queryVector,text_documentVector)
        
        title_cosineScores[document] = title_similarity
        text_cosineScores[document] = text_similarity
    
    title_cosineScores = dict(sorted(title_cosineScores.items(), key=lambda item: item[1],reverse=True)[:MAX_RESULTS])
    text_cosineScores = dict(sorted(text_cosineScores.items(), key=lambda item: item[1],reverse=True)[:MAX_RESULTS])

    combined_Scores = {}
    for (title_key,title_val),(text_key,text_val) in zip(title_cosineScores.items(),text_cosineScores.items()):
        if title_key in combined_Scores:
            combined_Scores[title_key] += ALPHA * title_val
        else:
            combined_Scores[title_key] = ALPHA * title_val
        
        if text_key in combined_Scores:
            combined_Scores[text_key] += BETA * text_val
        else:
            combined_Scores[text_key] = BETA * text_val
    
    pageRankScore = cursor.execute(
        f"""
            SELECT link_id, page_rank FROM link_2_id
            WHERE link_id IN ({",".join('?' for _ in combined_Scores)})
        """, tuple(combined_Scores.keys())).fetchall()
    
    combined_Scores = {page_id: score*pageRank for (page_id,score),(_,pageRank) in zip(combined_Scores.items(),pageRankScore)}
    combined_Scores = dict(sorted(combined_Scores.items(), key=lambda item: item[1],reverse=True)[:MAX_RESULTS])

    return combined_Scores



allDocs:list[int] = cursor.execute(
    """
        SELECT link_id FROM link_2_id                              
    """).fetchall()

for doc in allDocs:
    doc = doc[0]
    Title_globalPageDict[doc] = documentToVec(doc,True)
    Text_globalPageDict[doc] = documentToVec(doc)
    
    Title_globalPageStemText[doc] = cursor.execute(
        """
            SELECT k.keyword
            FROM link_2_id l
            JOIN web_info w ON l.link_id = w.link_id  
            JOIN forward_idx f ON w.link_id = f.link_id
            JOIN keyword_2_id k ON f.keyword_id = k.keyword_id
            WHERE l.link_id = ?;

        """,(doc,)).fetchone()[0]
    
    # Text_globalPageStemText[doc] = cursor.execute(
    #     """
    #         SELECT keyword FROM page_id_word_stem WHERE link_id = ?
    #     """,(doc,)).fetchone()[0]

for word_id,word in cursor.execute(
    """
        SELECT keyword_id, keyword FROM keyword_2_id
    """).fetchall():
    globalWordtoID[word] = word_id
