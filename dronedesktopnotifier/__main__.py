import datetime
import os
import platform
import re
import time
import urllib
from enum import Enum
from typing import List
from termcolor import colored

import click
import requests
import validators
from plyer import notification

from dronedesktopnotifier.requests_retry import requests_retry_session


def notify_mac(title, message, link, icon):
    t = "-title {!r}".format(title)
    m = "-message {!r}".format(message)
    o = "-open {!r}".format(link)
    i = "-appIcon {!r}".format(icon)
    os.system("terminal-notifier {}".format(" ".join([m, t, o, i])))


class Build:
    class state(Enum):
        unknown = 0
        running = 1
        failure = 2
        success = 3
        pending = 4
        cancelled = 5

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                if key == "status":
                    value = Build.state[dictionary[key]]
                else:
                    value = dictionary[key]
                setattr(self, key, value)

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __eq__(self, value):
        if value is None or getattr(self, "id") == None:
            return False
        return getattr(self, "id") == value.id


def get_time():
    return datetime.datetime.now().strftime("%a %H:%M:%S")


def notify(build: Build, link: str, balloon: bool, terminal_unicode: bool, terminal_color: bool) -> None:
    if build is None:
        return

    icon = None
    if build.status == Build.state.failure:
        icon = f"{__package__}\icons\state_failed.ico"
        symbol = "❌"
        color = "red"
    elif build.status == Build.state.running:
        icon = f"{__package__}\icons\state_running.ico"
        symbol = "🔄"
        color = "blue"
    elif build.status == Build.state.success:
        icon = f"{__package__}\icons\state_ok.ico"
        symbol = "✅"
        color = "green"
    else:
        return

    if terminal_unicode:
        s = symbol
    else:
        s = ""

    timestamp = get_time()
    text = f"{timestamp} {s}  `{build.status.name}` {link}{build.number} `{build.message}` {build.link_url} ({build.author})"

    if terminal_color:
        text = colored(text, color)

    # console
    print(text)

    # OS dependent notification
    if not balloon:
        return

    if platform.system() == "Darwin":
        notify_mac(title=f"{build.status.name} ", message=f"{build.message} ({build.author})", link=f"{link}{build.number}", icon=icon)
    elif platform.system() == "Windows":
        notification.notify(message=f"{symbol} {build.status.name} `{build.message}` ({build.author})", app_icon=icon)


def validate_names(ctx, name, value):
    r = re.compile(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$", re.IGNORECASE)

    names = value.strip().split()
    if any(len(n) == 0 for n in names):
        raise click.BadParameter(f"empty name(s) {names}")

    for n in names:
        if r.match(n) == None:
            raise click.BadParameter(f"invalid name `{n}`")

    return names


def validate_url(ctx, name, base_url):
    base_url = base_url.strip()
    if not validators.url(base_url):
        raise click.BadParameter(f"invalid url {base_url}")
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    split = urllib.parse.urlsplit(base_url)
    link = split[0] + "://" + split[1] + "/" + "/".join(split.path.split("/")[3:]) + "/"
    return base_url, link


def validate_drone_api(ctx, name, value):
    value = value.strip()
    regex = re.compile(r"^[a-zA-Z0-9]{36}\.[a-zA-Z0-9]{46}\.[a-zA-Z0-9]{43}$")
    if regex.match(value) is None:
        raise click.BadParameter(f"drone token is not valid {value}")

    return value


@click.command()
@click.option("--names", "-n", callback=validate_names, help="space delimited list of GitHub-account names that trigger the notification")
@click.option("--balloon/--no-balloon", default=True, help="if not set, no desktop notification is displayed")
@click.option("--delay", "-d", default=2, show_default=True, help="delay between updates")
@click.option("--delay", "-d", default=2, show_default=True, help="delay between updates")
@click.option("--terminal-unicode/--no-terminal-unicode", default=True, help="if set, unicode symbols will be used in the terminal output")
@click.option("--terminal-color/--no-terminal-color", default=True, help="if set, terminal output is colorful")
@click.argument("url", callback=validate_url)
@click.argument("drone-api-token", callback=validate_drone_api)
def drone_notifier(names, url, drone_api_token, balloon, delay, terminal_unicode, terminal_color):
    base_url, link = url

    # saving state builds
    old_my_builds = []

    skip_sleep = True
    showed_text_success = False
    showed_text_error = False
    while True:
        if skip_sleep:
            skip_sleep = False
        else:
            time.sleep(delay)

        # fetch info from drone api
        api_url = "{}/builds".format(base_url)
        headers = {"Authorization": f"Bearer {drone_api_token}"}
        try:
            r = requests_retry_session().get(api_url, headers=headers)
        except Exception as e:
            if not showed_text_error:
                showed_text_error = True
                text = f"{get_time()} failed to connect to  {base_url} : {e}"
                if terminal_color:
                    text = colored(text, "red")
                print(text)
            continue

        if r.status_code != 200:
            if not showed_text_error:
                showed_text_error = True
                text = f"{get_time()} error code #{r.status_code} from drone api: {r.reason}"
                if terminal_color:
                    text = colored(text, "red")
                print(text)
            continue

        try:
            builds = r.json()
        except:
            continue

        all_builds = [Build(b) for b in builds]
        my_builds: List[Build] = [b for b in all_builds if b.author in names]

        if not showed_text_success:
            showed_text_success = True
            text = f"{get_time()} got information for {len(builds)} builds from {base_url}, {len(my_builds)} are related to {names}"
            if terminal_color:
                text = colored(text, "green")
            print(text)

        # detect new elements that are pending or running
        for new_build in my_builds:
            if new_build not in old_my_builds and new_build.status in [Build.state.pending, Build.state.running]:
                notify(new_build, link, balloon, terminal_unicode, terminal_color)

        # detect status change
        for old_build in old_my_builds:
            if old_build not in my_builds:
                continue
            new_build = my_builds[my_builds.index(old_build)]
            if new_build.status != old_build.status:
                notify(new_build, link, balloon, terminal_unicode, terminal_color)

        old_my_builds = my_builds


if __name__ == "__main__":
    drone_notifier()
