import requests
import os
import argparse
import sys
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from clint.textui.progress import Bar as ProgressBar
import json
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = f"{os.environ.get('SERVER_HOST')}:{os.environ.get('SERVER_PORT')}"

"""
Get stats from the server by calling <host>:<port>/stats (HTTP GET)
"""
def stats():
  res = requests.get(os.path.join(SERVER_URL,'stats'))
  stats = json.loads(res.text)
  for key,val in stats.items():
      print(f"{key}: {val}")
  return res

def create_callback(encoder):
    expected_size = encoder.len
    def callback(monitor):
        bar = ProgressBar(expected_size=expected_size, filled_char='=')
        bar.show(monitor.bytes_read)
    return callback

"""
Upload a file by calling <host>:port/upload (HTTP POST). 
The method will read the contents of the file in chuncks and stream it to the server via HTTP POST with multipart/form-data.
A progress bar will be show the progress of the upload
"""
def upload_file(file_path):
    with open(file_path, 'rb') as file:
        e = MultipartEncoder(
            fields={'action': 'file', 'file': ('file', file, 'text/plain')}
        )        
        m = MultipartEncoderMonitor(e, create_callback(e))
        res = requests.post(os.path.join(SERVER_URL,'upload'), data=m, headers={'Content-Type': m.content_type})
        print(os.linesep)
        return res

"""
Upload a string by calling <host>:port/upload (HTTP POST). 
The method will send a string in chuncks and stream it to the server via HTTP POST with multipart/form-data.
A progress bar will be show the progress of the upload
"""
def upload_str(str):
    e = MultipartEncoder(
            fields={'action': 'str', 'str': str}
        )
    m = MultipartEncoderMonitor(e, create_callback(e))
    res = requests.post(os.path.join(SERVER_URL,'upload'), data=m, headers={'Content-Type': m.content_type})
    print(os.linesep)
    return res

"""
Send a URL to the server by calling <host>:port/upload (HTTP POST). The server will download the contents of the URL and parse the text.
"""
def upload_url(url):
    return requests.post(os.path.join(SERVER_URL,'upload'), data={'action': 'url', 'url': url})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='wordcount', description='Word Counter')
    parser.add_argument('action', choices=['upload', 'stats'], help='Type of action to execute')
    parser.add_argument('-f', help='File path')
    parser.add_argument('-u', help='URL')
    parser.add_argument('-s', help='String')
                        
    args = parser.parse_args()

    res = None
    if args.action == 'stats':
        res = stats()
    elif args.f:
        res = upload_file(args.f)
    elif args.u:
        res = upload_url(args.u)
    elif args.s:
        res = upload_str(args.s)
    else:
        sys.exit('Please specify a valid argument.')

    res.raise_for_status()
