# dronedesktopnotifier

`dronedesktopnotifier` is a Python library to get notifications from a drone.io-server on your desktop, it filters for names and can be used to only notify in command line or with balloon notifications (windows and mac supported).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dronedesktopnotifier.

```bash
pip install dronedesktopnotifier
```

- For mac and balloon notifications, install `terminal-notifier`

```bash
brew install terminal-notifier
```

## Usage

- Format

```bash
python -m dronedesktopnotifier https://drone.<yourdomain>.com/api/repos/<repo owner>/<repo name> <drone.io access token> --names <your github username(s)>
```

- Example

```bash
python -m dronedesktopnotifier https://drone.mycompany.io/api/repos/company/some-service jsgjijgjgojJGJISGJSGOSG.jtkjfjafkGSJGJOSGJOJSOGI.jksgoafjHGJAJGJKAGJ --names AlxndrJhn
```

### Arguments

- `url` this is the base url of the api of your `drone.ai` system, something like `https://drone.mycompany.io/api/repos/company/some-service`

- `drone-api-token` is your personal token from your `drone.io` system. You can find it at something like `https://drone.mycompany.io/account/token`
--no-terminal-color

### Optional parameters

- `-n` or `--names`
list of space separated names (your GitHub name for example) that should trigger the notification, if not given, all builds will trigger the alarm.

- `-d` or `--delay`
delay in seconds (integer) between `drone.ai` api requests.

- `--balloon/--no-balloon` in case you only want the terminal notification, the balloon is on by default.

- `--terminal-unicode/--no-terminal-unicode` in case you only want the terminal notifications in ascii, unicode is used by default.

- `--terminal-color/--no-terminal-color` in case you want colors in your terminal (requires `termcolor` package. Colors are on by default.

## Output

### The terminal output

```bash
Thu 14:08:15 got information for 50 builds from https://drone.mycompany.io/api/repos/company/some-service, 26 are related to ['AlxndrJhn']
Thu 14:08:15 🔄  `running` https://drone.mycompany.io/company/menu-service/2506 `My pull request title` https://github.com/company/some-service/pull/23 (AlxndrJhn)
```

There is one start-up message, it might be an error or as shown above, a success message.
If some build is pending or running, it will output it immediatly.

### The balloon output

1. For windows, it appears in to bottom right corner.
![popup example windows](https://raw.githubusercontent.com/AlxndrJhn/drone-desktop-notifier/master/docs/popup.PNG)

2. For mac, it appears in the top left corner, clicking it opens the default webbrowser to the build log directly.

## Known issues

none yet

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
