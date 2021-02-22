Word Count
================================================

## General

Word Count is a small utility that counts words in texts. It contains a client and server. The server receives texts via text files, raw strings or through urls and counts the number of occurances of each word in the text. All accurances are persisted on the server and accumulated across sessions.

## Components

Client - responsible for interacting with the client and passing the data to the web server. 
Server - receives text (files, strings, urls), parses them and stores the stats in a local json file.

## Prerequisites
- Python 3.8
- Make sure you have [pipenv](https://pypi.org/project/pipenv/) installed

## Installation
1. run `pipenv install`
2. run `pipenv shell`
3. run `chmod +x wc`

## Running
- To start the server run: `./wc server start`
- You can stop the server at any point by running: `./wc server stop`
- To upload a text file run: `./wc upload -f <file-path>`
- To upload a string run: `./wc upload -s <text>`
- To download the contents of a url containing text run: `./wc upload <url>`
- To stop the server run: `./wc server stop`

## Environment variables
You can set the following environment variables in .env file

`SERVER_HOST` - The host to the server. Default value is `localhost`

`SERVER_PORT` - Port to server. Default port is `8080` 










