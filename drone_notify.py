from plyer import notification
import requests
import click
from enum import Enum
import time
import datetime


class bstate(Enum):
    unknown = 0
    running = 1
    failure = 2
    success = 3


def notify(state: bstate, number: int):
    icon = None
    if state == bstate.failure:
        icon = 'state_failed.ico'
    elif state == bstate.running:
        icon = 'state_running.ico'
    else:
        icon = 'state_ok.ico'
    notification.notify(
        message=f'Build #{number} {state.name}',
        app_icon=icon
    )


if __name__ == '__main__':
    is_building = False
    last_running_builds = []
    myname = ''
    base_url = 'https://drone../api/repos//'
    link = 'https://drone..///'
    key = ''
    while True:
        # check drone
        url = '{}/builds'.format(base_url)
        headers = {'Authorization': f'Bearer {key}'}
        try:
            r = requests.get(url, headers=headers)
        except:
            time.sleep(1)
            continue
        if r.status_code == 200:

            try:
                builds = r.json()
            except:
                time.sleep(1)
                continue

            curr_builds = [(b['id'], bstate[b['status']], b['number'])
                           for b in builds if b['author'] == myname]

            # new
            new = [
                b for b in curr_builds if b not in last_running_builds and b[1] == bstate.running]
            if len(new) > 0:
                notify(bstate.running, new[0][0])
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                print(f'{timestamp} {new[0][1].name} {link}{new[0][2]}')

            # done
            for build in last_running_builds:
                cb = [b for b in curr_builds if b[0] == build[0]][0]
                if cb[1] != build[1]:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f'{timestamp} {cb[1].name} {link}{cb[2]}')
                    notify(cb[1], cb[0])

            last_running_builds = [
                b for b in curr_builds if b[1] == bstate.running]

        # if state changed, notify once
        time.sleep(2)
