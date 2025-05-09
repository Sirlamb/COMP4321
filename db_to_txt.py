def generate_spider_report():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    with open('spider.txt', 'w', encoding='utf-8') as f:
        c.execute('SELECT page_id, title, date, size FROM web_info')
        pages = c.fetchall()
        
        for page in pages:
            page_id, title, date, size = page
            
            # Get URL
            c.execute('SELECT link FROM link_2_id WHERE link_id = ?', (page_id,))
            url_row = c.fetchone()
            url = url_row[0] if url_row else "URL not found"
            
            # Get keywords with frequencies
            c.execute('''
                SELECT k.keyword, SUM(f.frequency) 
                FROM forward_idx f
                JOIN keyword_2_id k ON f.keyword_id = k.keyword_id
                WHERE f.page_id = ?
                GROUP BY k.keyword
            ''', (page_id,))
            keywords = [f"{row[0]} {row[1]}" for row in c.fetchall()]
            
            # Get parent links
            c.execute('''
                SELECT l.link 
                FROM parent_child p
                JOIN link_2_id l ON p.parent_id = l.link_id
                WHERE p.child_id = ?
            ''', (page_id,))
            parents = [row[0] for row in c.fetchall()]
            
            # Get child links
            c.execute('''
                SELECT l.link 
                FROM parent_child p
                JOIN link_2_id l ON p.child_id = l.link_id
                WHERE p.parent_id = ?
            ''', (page_id,))
            children = [row[0] for row in c.fetchall()]
            
            # Write to file
            f.write(f"score {page_id} {title}\n")
            f.write(f"{url}\n")
            f.write(f"{date}, {size} bytes\n")
            f.write("; ".join(keywords) + "\n\n")
            
            f.write("Parents:\n")
            if parents:
                for parent in parents:
                    f.write(f"{parent}\n")
            else:
                f.write("No parents\n")
            
            f.write("\nChildren:\n")
            if children:
                for child in children:
                    f.write(f"{child}\n")
            else:
                f.write("No children\n")
            
            f.write(f"\nscore {page_id} {title}\n")
            f.write("=" * 80 + "\n\n")
    
    conn.close()
    print("Report generated as spider.txt")

# Run the report generation
generate_spider_report()
print('txt generated')
