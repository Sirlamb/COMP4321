import requests
from bs4 import BeautifulSoup
import string
# from collections import Counter
import sqlite3
import time
import nltk
import spacy
from nltk.stem import PorterStemmer
from nltk import ngrams
from collections import Counter
from collections import defaultdict
import math


start_time = time.time()

# all_titles store the page title of all pages (I have included <h1> and <h2> as titles)
all_titles = []

# all_newwords stores the words appearing in the document (incleading subheadings and pointed form)
all_newwords = []

#fiinal_iterations is the no of iteration. Will stop when reach 30
final_iterations = 1
url = "testpage.htm"
#url = "ust_cse/PG.htm"

#all_hyperlink stores all hyperlinks
all_hyperlink = [url]

#finished_link store all scrapped links, so they will not be scrapped again
finished_link = [url]
hyperlink_storage = []

#last modified date
all_date = []


# this can do the Ngram, which will also be applied to the query
def phrase_extraction(anotherlist_var):
  bigrams = list(ngrams(anotherlist_var, 2))
  trigrams = list(ngrams(anotherlist_var, 3))

  bigram_strings = [' '.join(bigram) for bigram in bigrams]
  trigram_strings = [' '.join(trigram) for trigram in trigrams]

  # Count the frequency of each phrase
  bigram_freq = Counter(bigram_strings)
  trigram_freq = Counter(trigram_strings )
  if len(anotherlist_var)<30:
  # Filter out the phrase with frequency less than 2
    bigram_renew = [word for word in bigram_strings if bigram_freq[word] >= 2]
    trigram_renew = [word for word in trigram_strings if trigram_freq[word] >= 2]

  elif len(anotherlist_var)<100:
    bigram_renew = [word for word in bigram_strings if bigram_freq[word] >= 3]
    trigram_renew = [word for word in trigram_strings if trigram_freq[word] >= 3]
  elif len(anotherlist_var)<150:
    bigram_renew = [word for word in bigram_strings if bigram_freq[word] >= 4]
    trigram_renew = [word for word in trigram_strings if trigram_freq[word] >= 4]
  else:
    bigram_renew = [word for word in bigram_strings if bigram_freq[word] >= 5]
    trigram_renew = [word for word in trigram_strings if trigram_freq[word] >= 5]
  anotherlist_var.extend(bigram_renew)
  anotherlist_var.extend(trigram_renew)
  return anotherlist_var

def stemming_for_query(all_newwords_var):
  stemmer = PorterStemmer()
  nlp = spacy.load("en_core_web_sm")
  new_words_stemming_var = []
  for word_list in all_newwords_var:


    doc = nlp(word_list)

    temporary = []
    for token in doc:
      x = token.lemma_
      x = stemmer.stem(x)
      temporary.append(x)
    #combined_string = ' '.join(temporary)
    new_words_stemming_var.append(temporary)

  #new_words_stemming_var.append(storing_var)
  return new_words_stemming_var

# this is the stemming function, which will also be applied to the query
def stemming(all_newwords_var):
  stemmer = PorterStemmer()
  nlp = spacy.load("en_core_web_sm")
  new_words_stemming_var = []





  for word_list in all_newwords_var:
    storing_var = []

    for word in word_list:
      doc = nlp(word)
      if len(doc)==1:

        for token in doc:
          x = token.lemma_
          x = stemmer.stem(x)
          storing_var.append(x)
      else:
        temporary = []
        for token in doc:
          x = token.lemma_
          x = stemmer.stem(x)
          temporary.append(x)
        combined_string = ' '.join(temporary)
        storing_var.append(combined_string)
    new_words_stemming_var.append(storing_var)

  #return a list of stemmed words
  return new_words_stemming_var

def phrase_extraction_for_query(anotherlist_var):
  bigrams = list(ngrams(anotherlist_var, 2))
  trigrams = list(ngrams(anotherlist_var, 3))

  bigram_strings = [' '.join(bigram) for bigram in bigrams]
  trigram_strings = [' '.join(trigram) for trigram in trigrams]
  anotherlist_var.extend(bigram_strings)
  anotherlist_var.extend(trigram_strings)
  return anotherlist_var

def webcrawler(weblink,titles,hyperlink_all,newwords,iterations,finished_link_var):
  if iterations >= 25:

    return

  urls = f"https://www.cse.ust.hk/~kwtleung/COMP4321/{weblink}"
  # print(urls)
  print(iterations)
  response = requests.get(urls)
  soup = BeautifulSoup(response.content,'html.parser')

  words=[]
  anotherlist=[]

  # list modified date
  last_modified_date = response.headers.get('Last-Modified')
  if last_modified_date:
    all_date.append(last_modified_date)

  # find titles and store them in titles
  title1 = soup.find_all("h1")
  if title1:
    for link in title1:

      x = link.get_text(strip=True,separator=' ')
      x = ''.join(' ' if char in string.punctuation else char for char in x)

      x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
      x = ' '.join(x.split())
      y = x.split(" ")
      if y:
        y = [item for item in y if item]

        words.append(y)
      link.extract()
      #remove the headings1 and 2 from the doc after extracting them, afterwise will double mark them

  heading2 = soup.find_all("h2")
  if heading2:
    for link in heading2:

      x = link.get_text(strip=True,separator=' ')
      x = ''.join(' ' if char in string.punctuation else char for char in x)

      x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
      x = ' '.join(x.split())
      y = x.split(" ")
      if y:
        y = [item for item in y if item]


        words.append(y)
      link.extract()

  title_var = soup.find('title')
  title_var = title_var.get_text()
  titles.append(title_var)
  # print(title_var)
  #the title will be extracted using find_all("p")

  #store p string with words
  transcript = soup.find_all("p")
  # print("")

  hyperlink_var = []
  if transcript:
    for link in transcript:

      x = link.get_text(strip=True,separator=' ')

      #x = ''.join(' ' if char in string.punctuation else char for char in x)
      x = ''.join(' ' if char in string.punctuation else char for char in x)

      x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
      x = ' '.join(x.split())
      y = x.split(" ")
      if y:
        y = [item for item in y if item]


        words.append(y)


    #find all hyperlinks
      hyperlinks = link.find_all("a")
      if hyperlinks:
        # print("the newly added hyperlinks are")
        # print("")
        for hyperlinks2 in hyperlinks:
          link2 = hyperlinks2["href"]
          if link2.startswith("../"):
            link2 = link2[3:]
          hyperlink_var.append(link2)
          hyperlink_all.append(link2)

      link.extract()

  # print(hyperlink_var)
  hyperlink_storage.append(hyperlink_var)

  x = soup.get_text(strip=True,separator=' ')
  x = ''.join(' ' if char in string.punctuation else char for char in x)

  x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
  x = ' '.join(x.split())
  y = x.split(" ")
  if y:
    y = [item for item in y if item]


    words.append(y)

  
  for number in range(len(words)):
    anotherlist +=words[number]
    # put all list tgt to one list

  anotherlist = [word.lower() for word in anotherlist]

  anotherlist = phrase_extraction(anotherlist)

  newwords.append(anotherlist)
  # print("newly added words =", anotherlist)

  #recursive function
  for x in hyperlink_all[1:]:

    if x in finished_link_var:
      continue
    iterations+=1
    finished_link_var.append(x)
    webcrawler(x,titles,hyperlink_all,newwords,iterations,finished_link_var)

webcrawler(url,all_titles,all_hyperlink,all_newwords,final_iterations,finished_link)
# print("")
# print("titles are ", all_titles)
# print(len(all_titles))
# print("hyperlinks are", all_hyperlink)
# print(len(all_hyperlink))
# print("words are", all_newwords)
# print(len(all_newwords))



# stopword table

'''with open('stopwords.txt', 'r') as file:
    stopwords = file.read().splitlines()'''


with open('stopwords.txt', 'r') as file:
    stopwords = file.read().splitlines()



sizeofpage = []
frequency_position = []
cleaned_words = []
sizeofpagewoutstopword = []

for sublist in all_newwords:
  sizeofpage.append(int(len(sublist)))
  # need ask whether the size of the doc include stopwords we think it is without stopwords

  storing = []
  for wordlist in sublist:
    words = wordlist.split()
    num = 0
    for x in words:

      if x in stopwords or not x:

        num=1
        break
    if num==0:

      combined_string = ' '.join(words)
      storing.append(combined_string)
  cleaned_words.append(storing)
  sizeofpagewoutstopword.append(int(len(storing)))
#print(sizeofpagewoutstopword)

#here the old array all_newwords will be replaced by the new keywords array without stopwords
all_newwords = cleaned_words
'''
for x in all_newwords:
  for x_inside in x:
    if not x_inside:
      print("yes")'''


all_newwords = stemming(all_newwords)
'''
for x in all_newwords:
  for x_inside in x:
    if not x_inside:
      print("no")'''

term_freq_per_doc = []
for wordsindoc in all_newwords:
  # frequency and position
  temp = []
  term_freq = {}
  for i in range(len(wordsindoc)):
    word = wordsindoc[i]
    #if word not in stopwords:
    frequency = wordsindoc.count(word)
    temp.append([word, frequency, i])
    term_freq[word] = frequency
  frequency_position.append(temp)
  term_freq_per_doc.append(term_freq)


#title
#remove all punctuation in the title_list

#translator = str.maketrans('', '', string.punctuation)
#titles_wout_punct =  [sublist.translate(translator) for sublist in all_titles]
titles_wout_punct = []
for sublist in all_titles:
  x = ''.join(' ' if char in string.punctuation else char for char in sublist)
  x = ' '.join(x.split())  # Remove extra spaces between words

  titles_wout_punct.append(x)


titles_test = stemming_for_query(titles_wout_punct)
#print(titles_test)





content_terms = set()
title_terms = []
title_index = []
for x in titles_test :
  y = phrase_extraction_for_query(x)
  unique_title_terms = set(y)
  title_index.append(y)
  title_terms.append(unique_title_terms)

#now  title_terms is an list containing dictionaries with title words and phrase in that document


#term selection
# to do this, we form 2 dictionary. one stores term freqeuncy one stores doc frequency
doc_freq = defaultdict(int)
#term_tf = defaultdict(dict)
total_docs = len(hyperlink_storage)

# Calculate document frequency for non-title terms
for doc_idx, doc_keywords in enumerate(all_newwords):
    unique_terms = set(doc_keywords)
    content_terms.update(unique_terms)

    for term in unique_terms:
        if term not in title_terms:
            doc_freq[term] += 1
            #tf = term_freq_per_doc[doc_idx].get(term, 0)
            #term_tf[term][doc_idx] = tf


TFIDF_THRESHOLD = 0.02
removed_terms = []

for i in range(len(term_freq_per_doc)):

  for term, frequency_term in term_freq_per_doc[i].items():
    # get all the unique terms in each document and their term_frequency
    if term in title_terms[i]:
      continue
      #if the term is in title of that document, it should not be removed, so we should keep it
    term_document_frequency = doc_freq.get(term, 0)
    #get the document frequecy of the term
    idf = math.log((total_docs + 1) / (term_document_frequency + 1)) + 1
    document_size = sizeofpagewoutstopword[i]
    tf = frequency_term/document_size
    tfidf = tf * idf
    if tfidf <=TFIDF_THRESHOLD:
      filtered_list = [entry for entry in frequency_position[i] if entry[0] != term]
      frequency_position[i] = filtered_list
  #print(len(frequency_position[i]), end=' ')


#now, after the above coding, the aray frequency_position will remove the terms that shouldnt be treated as keywoords due to its low tfidf




# connect or create database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# clear old data
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for table_name in tables:
    c.execute(f"DROP TABLE IF EXISTS {table_name[0]};")
c.execute("VACUUM;")

# init database structure
c.execute('''
CREATE TABLE IF NOT EXISTS web_info (
    page_id INTEGER PRIMARY KEY,
    title TEXT,
    date TEXT,
    size INTEGER
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS forward_idx (
    page_id INTEGER,
    keyword_id INTEGER,
    frequency INTEGER,
    position INTEGER,
    PRIMARY KEY (page_id, keyword_id, position)
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS inverted_idx (
    keyword_id INTEGER,
    page_id INTEGER,
    PRIMARY KEY (page_id, keyword_id)
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS parent_child (
    parent_id INTEGER,
    child_id INTEGER,
    PRIMARY KEY (parent_id, child_id)
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS keyword_2_id (
    keyword_id INTEGER PRIMARY KEY,
    keyword TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS link_2_id (
    link_id INTEGER PRIMARY KEY,
    link TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS title_forward_index (
    page_id INTEGER,
    keyword_id INTEGER,
    frequency INTEGER,
    PRIMARY KEY (page_id, keyword_id),
    FOREIGN KEY (page_id) REFERENCES web_info(page_id),
    FOREIGN KEY (keyword_id) REFERENCES keyword_2_id(keyword_id)
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS title_inverted_index (
    keyword_id INTEGER,
    page_id INTEGER,
    frequency INTEGER,
    PRIMARY KEY (keyword_id, page_id),
    FOREIGN KEY (keyword_id) REFERENCES keyword_2_id(keyword_id),
    FOREIGN KEY (page_id) REFERENCES web_info(page_id)
)
''')
# prepare word id
keyword_id_map = {}
keyword_id_counter = 1
for words in frequency_position:
  for keyword, frequency, position in words:
    if keyword not in keyword_id_map:
      keyword_id_map[keyword] = keyword_id_counter
      c.execute('''
      INSERT OR REPLACE INTO keyword_2_id (keyword_id, keyword)
      VALUES (?, ?)
      ''', (keyword_id_counter, keyword))
      keyword_id_counter += 1

for doc_phrases in title_index:
    for phrase in doc_phrases:
        if phrase not in keyword_id_map:
            keyword_id_map[phrase] = keyword_id_counter
            c.execute('''
            INSERT OR REPLACE INTO keyword_2_id (keyword_id, keyword)
            VALUES (?, ?)
            ''', (keyword_id_counter, phrase))
            keyword_id_counter += 1

# prepare page id
page_id_map = {}
page_id_counter = 1
for link in finished_link:
  if link not in page_id_map:
    page_id_map[link] = page_id_counter
    current_link = "https://www.cse.ust.hk/~kwtleung/COMP4321/" + str(link)
    c.execute('''
    INSERT OR REPLACE INTO link_2_id (link_id, link)
    VALUES (?, ?)
    ''', (page_id_counter, current_link))
    page_id_counter += 1

# input data into database
for idx, (title, link, hyperlink, words, size, date) in enumerate(zip(all_titles, finished_link, hyperlink_storage, frequency_position, sizeofpage, all_date)):  # create web info table
  page_id = page_id_map[link]
  current_link = "https://www.cse.ust.hk/~kwtleung/COMP4321/" + str(link)
  c.execute('''
  INSERT OR REPLACE INTO web_info (page_id, title, date, size)
  VALUES (?, ?, ?, ?)
  ''', (page_id, title, date, size))


  title_phrases = title_index[idx]
  for phrase in title_phrases:

      phrase_counts = Counter(title_phrases)
      for phrase, count in phrase_counts.items():
        keyword_id = keyword_id_map[phrase]
      # Title forward index
        c.execute('''
          INSERT OR REPLACE INTO title_forward_index (page_id, keyword_id, frequency)
          VALUES (?, ?, ?)
          ''', (page_id, keyword_id, count))
        # Title inverted index
        c.execute('''
        INSERT OR IGNORE INTO title_inverted_index (keyword_id, page_id, frequency)
        VALUES (?, ?,?)
        ''', ( keyword_id, page_id, count))

  # create index
  for keyword, frequency, position in words:
    keyword_id = keyword_id_map[keyword]
    c.execute('''
    INSERT OR REPLACE INTO forward_idx (page_id, keyword_id, frequency, position)
    VALUES (?, ?, ?, ?)
    ''', (page_id, keyword_id, frequency, position))
    c.execute('''
    INSERT OR REPLACE INTO inverted_idx (keyword_id, page_id)
    VALUES (?, ?)
    ''', (keyword_id, page_id))

  # create link relationship
  for child in hyperlink:
    child_id = page_id_map[child]
    c.execute('''
    INSERT OR REPLACE INTO parent_child (parent_id, child_id)
    VALUES (?, ?)
    ''', (page_id, child_id))


conn.commit()
conn.close()
print('spider done')

end_time = time.time()
print('time used:', end_time-start_time)


