# -*- coding: UTF-8 -*-
import json
import requests
import time
import urllib

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['TELEGRAM']['TOKEN']
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# emotions and corressponding emojis
emoji = {
    "default": u'\U0001F600',
    "smile": u'\U0001F601',
    "sad": u'\U0001F62d',
    "love": u'\U0001F60d'
}
emotions = {
    "default": "neutral",
    "smile": "pleasant",
    "sad": "sad",
    "love": "love"
}
# keybaord layout setting
emotion_layout = [["default", "smile"],["sad", "love"]]

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    timeout = 100 # timeout for long polling connection
    url = URL + "getUpdates?timeout={}".format(timeout)
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.pathname2url(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            if text.lower() == "hi" or "hi " in text.lower():
                username = update["message"]["from"]["first_name"]
                msg = "Hi, {}. How are you?".format(username)
                keyboard = build_keyboard()
                send_message(msg, chat, keyboard)
            else :
                msg = update["message"]["text"]
                send_message(msg, chat)
        except Exception as e:
            print(e)

def get_emotion_query(emotion):
    return "{} ".format(emotions[emotion]) + emoji[emotion]

def build_keyboard():
    keyboard = []
    for row in emotion_layout:
        keyboard.append(map(get_emotion_query, row))
    reply_markup = {"keyboard":keyboard, "resize_keyboard": True, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        print updates
        if len(updates["result"]) > 0:
            try:
                echo_all(updates)
                last_update_id = get_last_update_id(updates) + 1
            except Execetion as e:
                print(e)
        time.sleep(1)

if __name__ == '__main__':
    main()
