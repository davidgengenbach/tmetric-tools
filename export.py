#!/usr/bin/env python

# Don't forget to do:

import json
import csv
import datetime
import math
import mechanicalsoup
import dateutil.parser
import dateutil.relativedelta
import time

def login(username, password):
    LOGIN_URL = 'https://app.tmetric.com/login'

    browser = mechanicalsoup.Browser(soup_config={"features":"html.parser"})
    page = browser.get(LOGIN_URL)
    login_form = page.soup.select("form")[0]

    login_form.select("#Username")[0]['value'] = username
    login_form.select("#Password")[0]['value'] = password

    URL = 'https://id.tmetric.com' + login_form.attrs['action']
    page = browser.submit(login_form, URL)
    form = page.soup.select('form')[0]
    page = browser.submit(form, form.attrs['action'])
    return browser


def datestr_to_datetime(s):
    return dateutil.parser.parse(s)

def timestamp(long_timestamp = False):
    fmt = '%y%m%d'
    if long_timestamp:
        fmt += '%H%M%S'
    return time.strftime(fmt, time.gmtime())

def get_entries(browser, start, end, group_id):
    TRACKING_ENTRY_URL = 'https://app.tmetric.com/api/timeentries/{}/group?endTime={end}&startTime={start}'.format(group_id, start = start, end = end)

    page = browser.get(TRACKING_ENTRY_URL)

    trackings = page.json()
    tracking_entries = []

    for user in trackings:
        username = user['userName']
        for entry in user['entries']:
            entry['userName'] = username
            if entry['endTime'] is None:
                continue
            start_time = datestr_to_datetime(entry['startTime'])
            end_time = datestr_to_datetime(entry['endTime'])
            duration = dateutil.relativedelta.relativedelta(end_time, start_time)
            entry['duration'] = '{}:{}'.format(duration.hours, str(duration.minutes).zfill(2))
            entry['timeReadable'] = start_time.strftime('%d.%m.%y\t%H:%M') + ' - ' + end_time.strftime('%H:%M')
            entry['description'] = entry['workTask']['description']
            del entry['workTask']
            tracking_entries.append(entry)

    tracking_entries.sort(key = lambda x: datestr_to_datetime(x['startTime']))
    return tracking_entries





user_data = open('user.txt').read().strip().split('\n')
user = user_data[0]
password = user_data[1]

# range of exported entries
start_time = '2016-11-01T23:00:00.000Z'
end_time = datetime.datetime.now().isoformat()

# when the first iteration started
iteration_start = datestr_to_datetime('2016-10-28T23:00:00.000Z')

browser = login(user, password)
entries = get_entries(browser, start = start_time, end = end_time, group_id = 11240)

total_time = 0
time_per_users = {}
for entry in entries:
    start_time = datestr_to_datetime(entry['startTime'])
    end_time = datestr_to_datetime(entry['endTime'])
    weeks_between = math.floor((start_time - iteration_start).days / 7)
    diff = (end_time - start_time).total_seconds() / 60
    total_time += diff
    username = entry['userName']
    if not username in time_per_users:
        time_per_users[username] = 0
    time_per_users[username] += (diff / 60)
    entry['week'] = weeks_between

for user, time_ in sorted(time_per_users.items(), key=lambda item: item[1]):
    user = user.replace('_', '.').replace('.', ' ').title()
    print('{:<6.0f} {}'.format(time_, user))

hours = math.floor(total_time / 60)
minutes = int(total_time % 60)

print("\n{:<6} Total".format('{}:{}'.format(hours, minutes)))

filename = 'out/{}_tracking_export'.format(timestamp())

with open(filename + '.csv', 'w') as f:
    HEADERS = ['week', 'userName', 'description', 'duration', 'timeReadable', 'startTime', 'endTime']
    csvwriter = csv.writer(f, quoting = csv.QUOTE_ALL)
    csvwriter.writerow(HEADERS)
    for entry in entries:
        csvwriter.writerow([entry[header] for header in HEADERS])

with open(filename + '.json', 'w') as f:
    json.dump(entries, f, indent = 4)