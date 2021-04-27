import sqlite3
from sqlite3 import Error
from werkzeug.datastructures import FileStorage

def convert_into_binary(file_path):
  print("[INFO] : converting into binary data rn")
  with open(file_path, 'rb') as file:
    binary = file.read()
  return binary

def write_to_file(binary_data, file_name):
  with open(file_name, 'wb') as file:
    file.write(binary_data)
  print("[DATA] : The following file has been written to file: ", file_name)

def read_blob_data(entryID):
  try:
    conn = sqlite3.connect('app.db')
    conn.text_factory = str  
    cur = conn.cursor()
    print("[INFO] : Connected to SQLite to read_blob_data")
    sql_fetch_blob_query = """SELECT * from uploads where id = ?"""
    cur.execute(sql_fetch_blob_query, (entryID,))
    record = cur.fetchall()
    for row in record:
      converted_file_name = row[1]
      photo_binarycode  = row[2]
      # parse out the file name from converted_file_name
      last_slash_index = converted_file_name.rfind("/") + 1 
      png_index = converted_file_name.find('.png')
      final_file_name = converted_file_name[last_slash_index:] 
      write_to_file(photo_binarycode, final_file_name)
      print("[DATA] : Image successfully stored on disk. Check the project directory. \n")
    cur.close()
  except sqlite3.Error as error:
    print("[INFO] : Failed to read blob data from sqlite table", error)
  finally:
    if conn:
        conn.close()
