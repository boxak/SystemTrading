import sqlite3

conn = sqlite3.connect('universe_price.db', timeout=10)
cur = conn.cursor()
sql = "insert into balance(code, bid_price, quantity, create_at, will_clear_at) values(?, ?, ?, ?, ?)"
cur.execute(sql, ('005930',70000,10,'20211120','today'))
conn.commit()

conn.close()

