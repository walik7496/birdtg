import asyncio
from flask import Flask, Response, render_template, request, jsonify, send_file
from flask_cors import CORS
from blackbird import findUsername
import logging
import requests
import telebot
import os
from threading import Thread
import json
import time

token = os.environ['token']
bot=telebot.TeleBot(token)
path = os.path.dirname(__file__)
app = Flask(__name__, static_folder='templates/static')
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app, resources={r"/*": {"origins": "*"}})
loop = asyncio.get_event_loop()
logging.getLogger('werkzeug').disabled = True


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"Hello ✌️ If you have any problems with the bot, follow the link: https://birdtg.sfallen.repl.co")

@bot.message_handler(content_types='text')
def message_reply(message):
    if len(message.text) > 1:
       os.system('python blackbird.py -u ' + message.text) 
       file = message.text + '.json'
       pathRead = os.path.join(path, 'results', file)
       f = open(pathRead, 'r')
       jsonD = json.load(f)
       bot.send_message(message.chat.id, f"Username: {jsonD['search-params']['username']}")
       time.sleep(5)
       bot.send_message(message.chat.id, f"Number of sites: {jsonD['search-params']['sites-number']}")
       time.sleep(5)
       #try:
       for u in jsonD['sites']:
         try:
           if u['status'] == "FOUND":
              bot.send_message(message.chat.id, f'[+]\033[0m - {u["app"]}\033[0m account found\033[0m - {u["url"]}\033[0m [{u["response-status"]}]\033[0m')
           time.sleep(5)
           if u["metadata"]:
              for d in u["metadata"]:
                  try:
                    bot.send_message(message.chat.id, f"   |--{d['key']}: {d['value']}")
                  except:
                    continue
         except:
           continue
       #except:
         #pass
                

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search/username' ,methods=["POST"])
def searchUsername():
    content = request.get_json()
    username = content['username']
    interfaceType = 'web'
    results = loop.run_until_complete(findUsername(username, interfaceType))
    return jsonify(results)

def run():
    app.run(host='0.0.0.0', port=9797)

def run_bot():
    bot.polling()

t = Thread(target=run)
rn = Thread(target=run_bot, daemon=True)

t.start()
rn.start()

t.join()