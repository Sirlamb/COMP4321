import requests
from bs4 import BeautifulSoup
import string
# from collections import Counter
import sqlite3
import time

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

def webcrawler(weblink,titles,hyperlink_all,newwords,iterations,finished_link_var):
  if iterations >30:
    return

  urls = f"https://www.cse.ust.hk/~kwtleung/COMP4321/{weblink}"
  # print(urls)
  # print(iterations)
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
      x = ''.join(char for char in x if char not in string.punctuation)
      x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
      y = x.split(" ")
      y = [entry for entry in y if entry]
      words.append(y)
      link.extract()

  heading2 = soup.find_all("h2")
  if heading2:
    for link in heading2:

      x = link.get_text(strip=True,separator=' ')
      x = ''.join(char for char in x if char not in string.punctuation)
      x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
      y = x.split(" ")
      y = [entry for entry in y if entry]
      words.append(y)
      link.extract()

  title_var = soup.find('title')
  title_var = title_var.get_text()
  titles.append(title_var)
  # print(title_var)

  #store p string with words
  transcript = soup.find_all("p")
  # print("")

  hyperlink_var = []
  for link in transcript:

    x = link.get_text(strip=True,separator=' ')
    x = ''.join(char for char in x if char not in string.punctuation)
    x = x.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t','')
    y = x.split(" ")
    y = [entry for entry in y if entry]
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
  x = ''.join(char for char in x if char not in string.punctuation)
  x = x.replace('\n', '').replace('\r', '').replace('\xa0','').replace('\t','')
  y = x.split(" ")
  y = [entry for entry in y if entry]
  # print("thru normal get text")

  # print(y)
  words.append(y)

  for number in range(len(words)):
    anotherlist +=words[number]

  anotherlist = [word.lower() for word in anotherlist]

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
with open('stopwords.txt', 'r') as file:
    stopwords = file.read().splitlines()

# remove stopword
sizeofpage = []
frequency_position = []
for wordsindoc in all_newwords:
  # size
  sizeofpage.append(int(len(wordsindoc)))

  # frequency and position
  temp = []
  for i in range(len(wordsindoc)):
    word = wordsindoc[i]
    if word not in stopwords:
      frequency = wordsindoc.count(word)
      temp.append([word, frequency, i])
  frequency_position.append(temp)

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
CREATE TABLE IF NOT EXISTS index_table (
    page_id INTEGER,
    keyword_id INTEGER,
    frequency INTEGER,
    position INTEGER,
    PRIMARY KEY (page_id, keyword_id, position)
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
for title, link, hyperlink, words, size, date in zip(all_titles, finished_link, hyperlink_storage, frequency_position, sizeofpage, all_date):
  # create web info table
  page_id = page_id_map[link]
  current_link = "https://www.cse.ust.hk/~kwtleung/COMP4321/" + str(link)
  c.execute('''
  INSERT OR REPLACE INTO web_info (page_id, title, date, size)
  VALUES (?, ?, ?, ?)
  ''', (page_id, title, date, size))

  # create index
  for keyword, frequency, position in words:
    keyword_id = keyword_id_map[keyword]
    c.execute('''
    INSERT OR REPLACE INTO index_table (page_id, keyword_id, frequency, position)
    VALUES (?, ?, ?, ?)
    ''', (page_id, keyword_id, frequency, position))

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
