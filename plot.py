#!/usr/bin/env python
from glob import glob
import json
import helper
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from pylab import rcParams
import datetime


sns.set_style("whitegrid")

USE_X_LIM = False
USE_Y_LIM = False

def get_ticks(min_date, max_date, days_between = 7):
    start_date = min_date
    current = min_date
    ticks = [current]
    while current < max_date:
        current = ticks[-1] + datetime.timedelta(days=days_between)
        ticks.append(current)
    return ticks

def plot(data):
    per_user = helper.get_per_user(data)
    per_user_acc = {}
    for user, entries in per_user.items():
        per_user_acc[user] = []
        for entry in entries:
            last = 0 if not len(per_user_acc[user]) else per_user_acc[user][-1]
            parts = entry['duration'].split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) / 60
            per_user_acc[user].append(last + hours + minutes)

    starttimes = [x['startTime'] for x in data]
    min_date = min(starttimes)
    max_date = max(starttimes)
    ticks = get_ticks(min_date, max_date)

    rcParams['figure.figsize'] = 12, 5

    for user, entries in per_user.items():
        times = per_user_acc[user]
        x = [min_date] + [x['startTime'] for x in entries] + [max_date]
        y = [0] + times + [times[-1]]
        plt.plot(x,y, label = user)
    plt.legend(loc='upper left')
    plt.gcf().autofmt_xdate()
    axes = plt.gca()

    if USE_X_LIM:
        axes.set_xlim([datetime.date(2016, 10, 1),datetime.date(2017, 4, 1)])

    if USE_Y_LIM:
        axes.set_ylim([0,270])
    axes.get_yaxis().tick_right()

    plt.savefig('plot.png')

if __name__ == '__main__':
    latest = helper.get_latest_data()
    plot(latest)