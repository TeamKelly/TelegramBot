import json
import random
import datetime
from firebase import firebase

with open('config.json', 'r') as f:
    config = json.load(f)

firebase = firebase.FirebaseApplication(config['DATABASE']['USER'], None)

def init_colors():
    colors = {
        1:{'r':255, 'g':0, 'b':0},
        2:{'r':127, 'g':127, 'b':0},
        3:{'r':0, 'g':255, 'b':0},
        4:{'r':0, 'g':127, 'b':127},
        5:{'r':0, 'g':0, 'b':255},
        6:{'r':127, 'g':0, 'b':127}}
    result = firebase.post('/colors', colors)

def add_new_user(username):
    new_user = {'name':username, 'mode':1}
    result = firebase.post('/users', new_user)

def get_user(username):
    url = '/users/' + config['DATABASE'][username]
    result = firebase.get(url, None)
    return result

def get_username2():
    url = '/demo/user2/name'
    result = firebase.get(url, None)
    return result

def get_url(username):
    return '/users/' + config['DATABASE'][username]

def get_today_emotions(username):
    dates = get_dates(username)
    today = extract_today(dates)
    return today['emotions']

def get_current_emotion(username):
    emotions = get_today_emotions(username)
    idx = get_current_idx()
    return emotions[idx]['emotion']

def most_common(lst):
    return max(set(lst), key=lst.count)

def get_date_with_random_colors(month, date):
    colors = []
    emotions = []
    for i in range(6):
        colors.append(random.randint(1,6))
        emotions.append({
            'emotion':"",
            'reason':""
        })
    return {
        'month':month,
        'date':date,
        'emotions':emotions,
        'colors':colors,
        'color':most_common(colors)
    }

def get_dates_with_random_colors(month, num_of_dates):
    dates = []
    for date in range(1,num_of_dates+1):
        dates.append(get_date_with_random_colors(month,date))
    return dates

# change I to He / am to is
def change_reason(reason):
    return reason.replace(" I ", " She ").replace(" i ", " she ").replace("I'm","She's").replace("i'm","she's").replace(" am ", " was ").replace("don't", "didn't").replace("my","her").replace("me","her").replace("mine","hers")

def get_reason(username, emotion):
    dates = get_dates(username)
    today = extract_today(dates)
    has_emotion = False
    for e in today['emotions']:
        if emotion == e['emotion']:
            has_emotion = True
            if e['reason'] != "":
                reason = e['reason']
                return change_reason(reason)
    if has_emotion:
        return "I don't know. She doesn't say why she was {}.".format(emotion)
    return "She wasn't {}.".format(emotion)

def update_mode(username, mode):
    url = get_url(username)
    result = firebase.put(url, 'mode', mode)

def update_dates(username, dates=None):
    if dates is None:
        today = datetime.datetime.today()
        dates = get_dates_with_random_colors(today.month, today.day)
        update_emotion(username, "", 1)
    url = get_url(username)
    result = firebase.put(url, 'dates', dates)

def extract_today(dates):
    today = datetime.datetime.today()
    for date in dates:
        if date['date'] == today.day:
            return date
    # if today doesn't exist, create it
    today =  get_date_with_random_colors(10, today.day)
    dates.append(today)
    return today

def get_current_idx():
    hour = datetime.datetime.now().hour
#    idx = (hour-9)/3
    idx = hour/4
    return int(idx)

def get_dates(username):
    user = get_user(username)
    return user['dates']

def update_emotion(username, emotion, color):
    dates = get_dates(username)
    today = extract_today(dates)
    idx = get_current_idx()
    today['colors'][idx] = color
    today['emotions'][idx]['emotion'] = emotion
    for i in range(idx+1,6):
        today['colors'][i] = 0
    update_dates(username, dates)

def update_reason(username, reason):
    dates = get_dates(username)
    today = extract_today(dates)
    idx = get_current_idx()
    today['emotions'][idx]['reason'] = reason
    update_dates(username, dates)

def main():
    #init_colors()
    #update_mode(username, 1)
    username1 = 'Yeongjin'
    username2 = 'sunju'
    username3 = 'Taehee'
    update_dates(username1)
    update_dates(username2)
    update_dates(username3)

if __name__ == '__main__':
    main()
