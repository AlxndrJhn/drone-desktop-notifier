import datetime
import os
import platform
import re
import time
import urllib
from enum import Enum
from typing import List

import click
import requests
import validators
from plyer import notification
from termcolor import colored

from .requests_retry import requests_retry_session


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

    def get_link(self):
        return f'{self.api_url[:-3]}{self.repo_full_name}/{self.number}'


def get_time():
    return datetime.datetime.now().strftime("%a %H:%M:%S")


def notify(
    build: Build, balloon: bool, terminal_unicode: bool, terminal_color: bool
) -> None:
    if build is None:
        return
    link = build.get_link()
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
    text = f"{timestamp} {s}  `{build.status.name}` {link} `{build.message}` {build.link_url} ({build.author})"

    if terminal_color:
        text = colored(text, color)

    # console
    print(text)

    # OS dependent notification
    if not balloon:
        return

    if platform.system() == "Darwin":
        notify_mac(
            title=f"{build.status.name} ",
            message=f"{build.message} ({build.author})",
            link=f"{link}",
            icon=icon,
        )
    elif platform.system() == "Windows":
        notification.notify(
            message=f"{symbol} {build.status.name} `{build.message}` ({build.author})",
            app_icon=icon,
        )


def validate_names(ctx, name, value):
    if value is None:
        return None

    r = re.compile(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$", re.IGNORECASE)

    names = value.strip().split()
    if any(len(n) == 0 for n in names):
        raise click.BadParameter(f"empty name(s) `{names}`")

    for n in names:
        if r.match(n) == None:
            raise click.BadParameter(f"invalid name `{n}`")

    return names


def validate_url(ctx, name, base_url):
    base_url = base_url.strip()
    if not validators.url(base_url):
        raise click.BadParameter(f"invalid url {base_url}")
    base_url = base_url.strip("/")
    if not base_url.lower().endswith("api"):
        raise click.BadParameter(f"`{base_url}` must contain `api` at the end")
    return base_url


def validate_drone_api(ctx, name, value):
    value = value.strip()
    regex = re.compile(r"^[a-zA-Z0-9]{30,50}\.[a-zA-Z0-9]{30,50}\.[a-zA-Z0-9]{30,50}$")
    if regex.match(value) is None:
        raise click.BadParameter(f"drone token is not valid `{value}`")

    return value


@click.command()
@click.option(
    "--names",
    "-n",
    callback=validate_names,
    help="space delimited list of GitHub-account names that trigger the notification",
)
@click.option(
    "--balloon/--no-balloon",
    default=True,
    help="if not set, no desktop notification is displayed",
)
@click.option(
    "--delay", "-d", default=2, show_default=True, help="delay between updates"
)
@click.option(
    "--terminal-unicode/--no-terminal-unicode",
    default=True,
    help="if set, unicode symbols will be used in the terminal output",
)
@click.option(
    "--terminal-color/--no-terminal-color",
    default=True,
    help="if set, terminal output is colorful",
)
@click.argument("url", callback=validate_url)
@click.argument("drone-api-token", callback=validate_drone_api)
def drone_notifier(
    names, url, drone_api_token, balloon, delay, terminal_unicode, terminal_color
):
    headers = {"Authorization": f"Bearer {drone_api_token}"}
    # get all registered repos
    showed_text_error = False
    while True:
        try:
            r = requests_retry_session().get(url + "/user/repos", headers=headers)
            if r.status_code == 200:
                repos_candidates = r.json()
                break
        except Exception:
            if not showed_text_error:
                showed_text_error = True
                text = f"{get_time()} failed to connect to  {url} : {e}"
                if terminal_color:
                    text = colored(text, "red")
                print(text)
            continue
    if len(repos_candidates) == 0:
        raise RuntimeError(f"No repositories found on `{url}`")

    # get only active repos (last build younger than 30 days)
    print(f'{get_time()} Checking {len(repos_candidates)} repositories for activity (last 30 days)')
    repo = repos_candidates.pop()
    repos = []
    showed_text_error = False
    while True:
        try:
            r = requests_retry_session().get(
                f'{url}/repos/{repo["full_name"]}/builds', headers=headers
            )
            assert r.status_code == 200

            showed_text_error = False

            builds = r.json()

            if len(builds) == 0:
                repos.append(repo)
                if repos_candidates:
                    repo = repos_candidates.pop()
                    continue
                else:
                    break

            latest_build = builds[0]
            diff_days = (time.time() - latest_build["created_at"]) / (24 * 3600)
            if diff_days <= 30:
                repos.append(repo)

            if repos_candidates:
                repo = repos_candidates.pop()
            else:
                break
        except Exception:
            if not showed_text_error:
                showed_text_error = True
                text = f"{get_time()} failed to connect to  {url} : {e}"
                if terminal_color:
                    text = colored(text, "red")
                print(text)

    if len(repos) == 0:
        raise RuntimeError(f"No active repositories found on `{url}`")
    print(f'{get_time()} Active repositories found:', [repo["full_name"] for repo in repos])

    # saving state builds
    old_my_builds = []

    skipped_first_sleep = False
    showed_text_success = False
    showed_text_error = False
    while True:
        # start quickly on start-up
        if skipped_first_sleep:
            time.sleep(delay)
        skipped_first_sleep = True

        # get all builds from all repos
        all_builds = []
        for repo in repos:
            # fetch info from drone api
            showed_text_error = False
            while True:
                try:
                    r = requests_retry_session().get(
                        f'{url}/repos/{repo["full_name"]}/builds', headers=headers
                    )
                    assert r.status_code == 200
                    build_dicts = r.json()
                    all_builds.extend([Build(b, repo_full_name=repo["full_name"], api_url=url) for b in build_dicts])
                    break
                except Exception as e:
                    if not showed_text_error:
                        showed_text_error = True
                        text = f"{get_time()} failed to connect to  {url} : {e}"
                        if terminal_color:
                            text = colored(text, "red")
                        print(text)
                    continue

        my_builds: List[Build] = [
            b for b in all_builds if b.author in names
        ] if names else all_builds

        if not showed_text_success:
            showed_text_success = True
            if names:
                names_segment = f", {len(my_builds)} are related to {names}"
            else:
                names_segment = (
                    ", triggering on all builds (consinder the --names option)"
                )
            text = f"{get_time()} got information for {len(all_builds)} builds from {url}{names_segment}"
            if terminal_color:
                text = colored(text, "green")
            print(text)

        # detect new elements that are pending or running
        for new_build in my_builds:
            if new_build not in old_my_builds and new_build.status in [
                Build.state.pending,
                Build.state.running,
            ]:
                notify(new_build, balloon, terminal_unicode, terminal_color)

        # detect status change
        for old_build in old_my_builds:
            if old_build not in my_builds:
                continue
            new_build = my_builds[my_builds.index(old_build)]
            if new_build.status != old_build.status:
                notify(new_build, balloon, terminal_unicode, terminal_color)

        old_my_builds = my_builds


if __name__ == "__main__":
    drone_notifier()
