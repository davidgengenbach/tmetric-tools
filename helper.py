import json
import csv
import datetime
import mechanicalsoup
import dateutil.parser
import dateutil.relativedelta
import time
import math
from glob import glob

def get_latest_data():
    files = glob('out/*.json')
    files.sort()
    with open(files[-1], 'r') as f:
        d = json.load(f)
        convert_to_datetimes(d)
        return d

def convert_to_datetimes(data):
    for entry in data:
        entry['endTime'] = datestr_to_datetime(entry['endTime'])
        entry['startTime'] = datestr_to_datetime(entry['startTime'])

def datestr_to_datetime(s):
    return dateutil.parser.parse(s)

def get_per_user(data):
    per_user = {}
    for entry in data:
        username = entry['userName']
        if not username in per_user:
            per_user[username] = []
        per_user[username].append(entry)
    return per_user
