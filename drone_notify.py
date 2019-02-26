import plyer
import requests
import click
from enum import Enum
import time
import datetime

import os

def notify_mac(title, message, link, icon):
    t = "-title {!r}".format(title)
    m = "-message {!r}".format(message)
    o = "-open {!r}".format(link)
    i = "-appIcon {!r}".format(icon)
    os.system("terminal-notifier {}".format(" ".join([m, t, o, i])))


class bstate(Enum):
    unknown = 0
    running = 1
    failure = 2
    success = 3
    pending = 4
    cancelled = 5


def notify(state: bstate, number: int, link: str):
    icon = None
    if state == bstate.failure or state == bstate.cancelled:
        icon = "state_failed.ico"
    elif state == bstate.running:
        icon = "state_running.ico"
    else:
        icon = "state_ok.ico"

    notify_mac(title=f"{state.name}", message=f"{number}", link=f"{link}", icon=icon)


if __name__ == "__main__":
    last_running_builds = []
    while True:
        # check drone
        url = "{}/builds".format(base_url)
        headers = {"Authorization": f"Bearer {key}"}
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

            curr_builds = [
                (b["id"], bstate[b["status"]], b["number"])
                for b in builds
                if b["author"] == myname
            ]

            # new
            new = [
                b
                for b in curr_builds
                if b not in last_running_builds and b[1] == bstate.running
            ]
            if len(new) > 0:
                notify(new[0][1], new[0][0], f'{link}{new[0][2]}')
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"{timestamp} {new[0][1].name} {link}{new[0][2]}")

            # done
            for build in last_running_builds:
                cb = [b for b in curr_builds if b[0] == build[0]][0]
                if cb[1] != build[1]:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"{timestamp} {cb[1].name} {link}{cb[2]}")
                    notify(cb[1], cb[0], f'{link}{cb[2]}')

            last_running_builds = [b for b in curr_builds if b[1] == bstate.running]

        # if state changed, notify once
        time.sleep(2)
