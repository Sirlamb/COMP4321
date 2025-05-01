import sqlite3

tables = ['web_info', 'forward_idx', 'inverted_idx', 'parent_child', 'keyword_2_id', 'link_2_id']
# web_info: page_id, title, date, size
# forward_idx: page_id, keyword_id, frequency, position
# inverted_idx, keyword_id, page_id
# parent_child: parent_id, child_id
# keyword_2_id: keyword_id, keyword
# link_2_id: link_id, link

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

for table in tables:
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    print(table)
    for row in rows:
        print(row)
    print('\n')

connection.close()

# use the follow code for searching
# SELECT * FROM table_name WHERE colume_name < 2 AND colume_name = 'apple';
