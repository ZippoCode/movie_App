import sqlite3

database_path = 'db.sqlite3'
table_name = 'movies_movie_genres'

try:
    connection = sqlite3.connect(database_path)
    print("Connected to SQLite")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print("Column Names:", column_names)

    for row in rows:
        print(row)

except sqlite3.Error as error:
    print("Error while connecting to SQLite", error)

finally:
    if connection:
        connection.close()
        print("The SQLite connection is closed")
