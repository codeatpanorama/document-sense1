import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
import uuid
import pandas as pd
import reader
import asyncio


app = Flask('__main__')
UPLOAD_FOLDER = './data/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello():
    name = 'Rosalia'
    return render_template('index.html', title='Welcome', username=name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods= ['POST'])
def upload():
    requestId = str(uuid.uuid4())
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        asyncio.run(reader.main())
        
        # Data to be written
        dictionary = [{
            "request-id": requestId,
            "status": "uploaded"
        }]
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

        return dictionary[0]

@app.route("/health")
def health():
    return {"status": "up"}

@app.route("/request/<id>")
def getRequest(id):
    # Opening JSON file
    f = open('sample.json')
    data = json.load(f)
    output_dict = [x for x in data if x['request-id'] == id]
    return output_dict[0]



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)


#export FLASK_APP=app/app.py 
# flask run