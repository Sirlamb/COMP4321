import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute(f'SELECT COUNT(*) FROM web_info')
number_of_page = cursor.fetchone()[0]

with open('spider_result.txt', 'w', encoding='utf-8') as file:
    for link_id in range(1, number_of_page+1):
        # background info
        cursor.execute(f'SELECT * FROM web_info WHERE page_id = {link_id}')
        _, title, date, size = cursor.fetchone()
        cursor.execute(f'SELECT * FROM link_2_id WHERE link_id = {link_id}')
        _, url = cursor.fetchone()
        file.write(title + '\n')
        file.write(url + '\n')
        file.write(date + ', ' + str(size) + '\n')

        # keyword info
        cursor.execute(f'SELECT * FROM index_table WHERE page_id = {link_id}')
        rows = cursor.fetchall()
        for row in rows[:10]:
            _, keyword_id, frequency = row
            cursor.execute(f'SELECT * FROM keyword_2_id WHERE keyword_id = {keyword_id}')
            _, keyword = cursor.fetchone()
            file.write(keyword + ' ' + str(frequency) + '; ')
        file.write('\n')

        # child info
        cursor.execute(f'SELECT * FROM parent_child WHERE parent_id = {link_id}')
        rows = cursor.fetchall()
        for row in rows[:10]:
            _, child_id = row
            cursor.execute(f'SELECT * FROM link_2_id WHERE link_id = {child_id}')
            _, url = cursor.fetchone()
            file.write(url + '\n')

        file.write('----------\n')
