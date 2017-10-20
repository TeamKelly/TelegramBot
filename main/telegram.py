# -*- coding: UTF-8 -*-
import json
import requests
import time
import urllib
import codecs
import emotion_groups
import database

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['TELEGRAM']['TOKEN']
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
# status = 1 when asking for changing
# status = 2 when asking why he/she feels like that
status = 0
emotion_to_emoji = {}
emotion_to_group = {}
group_to_number = {
    "JOY":1,
    "SADNESS":2,
    "DISGUST":3,
    "FEAR":4,
    "ANGER":5,
    "LOVE":6
}
group_to_msg = {
    1:"Oh, you are {}! Happy to hear that :)",
    2:"Are you {}? why? :'(",
    3:"Are you {}? why?",
    4:"Are you {}? why?",
    5:"Are you {}? why?",
    6:"Oh, you are {}! I envy you!! XD"
}
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

def check_calendar(username, chat):
    global status
    database.update_mode(username, 0)
    msg = "Please check your calendar. Do you want to change the calendar to yours?"
    send_message(msg, chat)
    status = 1

def check_yes(text):
    yes_words = ["yes", "sure", "okay", "ok", "of course"]
    for word in yes_words:
        if word in text:
            return True
    return False

def echo_all(updates):
    global status
    for update in updates["result"]:
        check_mode_change = (status == 1)
        check_reason = (status == 2)
        status = 0
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            username = update["message"]["from"]["first_name"]
            username2 = database.get_username2()
            text = text.lower()

            # when he want to change back calendar to his
            if check_mode_change and check_yes(text):
                database.update_mode(username, 1)
                msg = "Okay, I changed."
                send_message(msg, chat)
                return

            # when he wants to check her emotions
            if "how is she" in text:
                if "now" in text:
                    emotion = database.get_current_emotion(username2)
                    if emotion == "":
                        msg = "I don't know.. She didn't tell me how she is today."
                        send_message(msg, chat)
                    else:
                        msg = "She is {}.".format(emotion)
                        send_message(msg, chat)
                        check_calendar(username, chat)
                else:
                    emotions = database.get_today_emotions(username2)
                    emots = []
                    for e in emotions:
                        emotion = e['emotion']
                        if emotion == "":
                            continue
                        if len(emots) == 0 or emots[-1] != emotion:
                            emots.append(emotion)
                    if len(emots) == 0:
                        msg = "I don't know.. She didn't tell me how she is today."
                        send_message(msg, chat)
                        return
                    elif len(emots) == 1:
                        msg = "She is {}.".format(emots[0])
                    else:
                        msg = "She was {}, but {} now.".format(emots[-2], emots[-1])
                    send_message(msg, chat)
                    check_calendar(username, chat)
                return

            # when he/she explains the reason of the feeling
            if check_reason and "because" in text:
                database.update_reason(username, text)
                msg = "Oh.. sorry to hear that. Cheer up, {}!".format(username)
                send_message(msg, chat)
                return

            # when he/she talks about his/her emotion
            for emotion in emotion_to_emoji.keys():
                if emotion in text:

                    # when he asks why she felt like that
                    if "why" in text and "she" in text:
                        msg = database.get_reason(username2, emotion)
                        send_message(msg, chat)
                        return
                    group = emotion_to_group[emotion]
                    database.update_emotion(username, emotion, group)
                    msg = group_to_msg[group].format(emotion)
                    send_message(msg, chat)
                    status = 2
                    return

            if text == "hi" or "hi " in text or "kelly" in text:
                msg = "Hi, {}. How are you?".format(username)
                keyboard = build_keyboard()
                send_message(msg, chat, keyboard)
            else:
                msg = update["message"]["text"]
                send_message(msg, chat)
        except Exception as e:
            print(e)

def get_emotion_query(emotion):
    return emotion + " " + emotion_to_emoji[emotion]

def build_keyboard():
    keyboard = []
    emotion_layout = [["excited", "satisfied", "joyful", "love"],
                      ["morose", "crying", "gloomy", "lonely"],
                      ["depressed", "disappointed", "scared", "pouting"]]
    for row in emotion_layout:
        keyboard.append(map(get_emotion_query, row))
    reply_markup = {"keyboard":keyboard, "resize_keyboard": True, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_emotions():
    groups = emotion_groups.getEmotions()
    for group in groups:
        emotions = groups[group]
        for emotion in emotions:
            emotion_to_emoji[emotion] = emotions[emotion]
            emotion_to_group[emotion] = group_to_number[group]

def main():
    last_update_id = None
    build_emotions()
    while True:
        updates = get_updates(last_update_id)
        print updates
        if len(updates["result"]) > 0:
            try:
                echo_all(updates)
                last_update_id = get_last_update_id(updates) + 1
            except Exception as e:
                print(e)
        time.sleep(1)

if __name__ == '__main__':
    main()
