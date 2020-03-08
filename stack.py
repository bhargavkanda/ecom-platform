import psycopg2
conn = psycopg2.connect("dbname = 'zapyle_db' user = 'zapadmin' host = 'localhost' password = 'zapy!e1234'")
cur = conn.cursor()
cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
tables = [i[0] for i in cur.fetchall()]
conn.close()

for i in tables:
    print i
    try:
        conn = psycopg2.connect("dbname = 'zapyle_db' user = 'zapadmin' host = 'localhost' password = 'zapy!e1234'")
        cursor = conn.cursor()
    #print "SELECT MAX(id) FROM {};".format(i[0])
    
        cursor.execute("SELECT MAX(id) FROM {};".format(i))
        val = cursor.fetchall()[0][0]
	conn.close()
        if val:
            print ">>>>>"
	    conn = psycopg2.connect("dbname = 'zapyle_db' user = 'zapadmin' host = 'localhost' password = 'zapy!e1234'")
            cursor = conn.cursor()
            cur.execute('ALTER SEQUENCE {}_id_seq RESTART WITH {}'.format(i, cursor.fetchall()[0][0]))
            conn.commit()
	    
        conn.close()
    except:
        pass
#cur.execute('ALTER SEQUENCE {}_id_seq RESTART WITH max(id)'.format(i[0]))
#cur.commit()
conn.close()
