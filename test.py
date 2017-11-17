import datetime


start_date = '04.11.16'
end_date = datetime.datetime.now() + datetime.timedelta(days=7)
current = datetime.datetime.strptime(start_date, "%d.%m.%y")
ticks = [current]
while current < end_date:
    current = ticks[-1] + datetime.timedelta(days=14)
    ticks.append(current)

print(ticks)