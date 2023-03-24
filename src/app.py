from flask import Flask

from extract import reader

from db import database

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello"


@app.route("/extract", methods=['POST'])
def extract():

    # this will hold all the logic for text extarction and will return a values to insert into db
    values = reader.extract("test")
    
    connnection = database.connect()

    cursor = connnection.cursor()

    for value in values:
        cursor.execute("INSERT INTO WORDS(page_id, text, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s, %s)", value)

    # commit the changes to the database
    connnection.commit()

    # close the cursor and connection objects
    cursor.close()
    connnection.close()

    return "extract started"


@app.route("/generatebound", methods=['GET'])
def search():
    return "bounding started"



if __name__ == '__main__':
    app.run(debug=True)