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
    print result

def add_new_user(username):
    new_user = {'name':username, 'mode':1}
    result = firebase.post('/users', new_user)
    print result

def get_user(username):
    url = '/users/' + config['DATABASE'][username]
    result = firebase.get(url, None)
    return result

def get_url(username):
    return '/users/' + config['DATABASE'][username]

def most_common(lst):
    return max(set(lst), key=lst.count)

def get_date_with_random_emotions(month, date):
    emotions = []
    for i in range(6):
        emotions.append(random.randint(1,6))
    return {
        'month':month,
        'date':date,
        'emotions':emotions,
        'rep_emotion':most_common(emotions)
    }

def get_dates_with_random_emotions(month, num_of_dates):
    dates = []
    for date in range(1,num_of_dates+1):
        dates.append(get_date_with_random_emotions(month,date))
    return dates

def update_mode(username, mode):
    url = get_url(username)
    result = firebase.put(url, 'mode', mode)
    print "update_mode"
    print result

def update_dates(username, dates=None):
    if dates is None:
        today = datetime.datetime.today()
        dates = get_dates_with_random_emotions(today.month, today.day)
    url = get_url(username)
    result = firebase.put(url, 'dates', dates)
    print "update_dates"
    print result

def extract_today(dates):
    today = datetime.datetime.today()
    for date in dates:
        if date['date'] == today.day:
            return date
    return None

def main():
    #init_colors()
    #update_mode(username, 1)
    username = 'yeongjin'
    update_dates(username)
    user = get_user(username)
    today = extract_today(user['dates'])
    print today

if __name__ == '__main__':
    main()
