from flask import Flask, flash, request, redirect, url_for
import os
import pathlib
import uuid
import requests
from pathlib import Path
import re
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

#Path to current file
WORKING_DIR = pathlib.Path().absolute()

#Path to dir containing uploaded files
UPLOAD_DIR= os.environ.get('UPLOAD_FILE_PATH', os.path.join(WORKING_DIR, '.downloads'))

#Path of the dir containing the stats json file
OUTPUT_DIR= os.environ.get('OUTPUT_FILE_PATH', os.path.join(WORKING_DIR, '.output'))

STATS_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../.output/', 'stats.json')

#Generate paths if they do not exist
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

"""
Clean the string and count the number of occurrences of each word. Persist the counts in COUNTS_FILE_PATH in a json format.
"""
def update_count(str):
    #This will strip Mid word dashes, commas and digits as described in the task although I think the intention was to remove anything that is not a letter
    #str = re.sub(r'[-,\d]|(?<=\w)-(?=\w)', '', str.lower())
    str = re.sub(r'[^a-zA-Z\s+]', '', str.lower())
    res = {}
    for w in str.split():
        if w not in res:
            res[w] = 0
        res[w] += 1
    
    if os.path.exists(STATS_FILE_PATH):
        with open(STATS_FILE_PATH, 'r') as f:
            counts = json.loads(f.read())
            
            for w in res:
                if w in counts:
                    res[w] += counts[w]
    
    with open(STATS_FILE_PATH, 'w') as f:
        json.dump(res, f) 

"""
Returns the stats stored in STATS_FILE_PATH. 
"""
@app.route("/stats", methods=['GET'])
def stats():
    if os.path.exists(STATS_FILE_PATH):
        with open(STATS_FILE_PATH, 'r') as f:
            return json.loads(f.read())
    else:
        return 'No stats yet :/'

"""
Upload text by passing a text-file, string, or a URL containing text.
"""
@app.route("/upload", methods=['POST'])
def upload():
    try:
        if request.method == 'POST':
            filename = os.path.join(UPLOAD_DIR, str(uuid.uuid4()))
            action = request.form['action']
            if (action == 'file'):
                if 'file' not in request.files:
                    return 'No file specified', 500
                file = request.files['file']
                file.save(filename)
                
                #Move cursor to beginning of file after it was read
                file.seek(0)
                update_count(file.stream.read().decode('utf-8'))
                status = "Ok"
            elif (action == 'str'):
                string = request.form.get('str')
                if string:
                    with open(filename, "w") as text_file:
                        text_file.write(string)
                    update_count(string)
                    status = "Ok"
                else:
                    status = f"No valid string was passed", 500
                pass
            elif (action == 'url'):
                url = request.form.get('url')
                if url:
                    r = requests.get(url, allow_redirects=True)
                    content = r.content.decode('utf-8')
                    with open(filename, "w") as text_file:
                        text_file.write(content)
                    update_count(content)
                    status = "Ok"
                else:
                    status = f"No valid URL was passed", 500
            else:
                status = f"Unrecognized action \"{action}\"", 500
    except Exception as e:
        status = str(e), 500
    finally:
        return status


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.config['UPLOAD_DIR'] = UPLOAD_DIR
    app.run(host='0.0.0.0', port=os.environ.get('SERVER_PORT'))