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
python -m dronedesktopnotifier https://drone.<yourdomain>.com/api <drone.io access token> --names <your github username(s)>
```

- Example

```bash
python -m dronedesktopnotifier https://drone.mycompany.io/api jsgjijgjgojJGJISGJSGOSG.jtkjfjafkGSJGJOSGJOJSOGI.jksgoafjHGJAJGJKAGJ --names AlxndrJhn
```

### Arguments

- `url` this is the base url of the api of your `drone.ai` system, something like `https://drone.mycompany.io/api`, it will get all active repositories automatically

- `drone-api-token` is your personal token from your `drone.io` system. You can find it at something like `https://drone.mycompany.io/account/token`

### Optional parameters

- `-n` or `--names`
list of space separated names (your GitHub name for example) that should trigger the notification, if not given, all builds will trigger the alarm.

- `-d` or `--delay`
delay in seconds (integer) between `drone.ai` api request batches.

- `--balloon/--no-balloon`
in case you only want the terminal notification, the balloon is on by default.

- `--terminal-unicode/--no-terminal-unicode`
in case you only want the terminal notifications in ascii, unicode is used by default.

- `--terminal-color/--no-terminal-color`
in case you want colors in your terminal (requires `termcolor` package. Colors are on by default.

## Output

### The terminal output

```bash
Fri 12:08:59 Checking 14 repositories for activity (last 30 days)
Fri 12:09:01 Active repositories found: ['mycompany/some-service', 'mycompany/some-ai', 'mycompany/labelstuff', 'mycompany/inspect_stuff', 'mycompany/cnn-stuff']
Fri 12:09:02 got information for 250 builds from https://drone.mycompany.io/api, 48 are related to ['AlxndrJhn']
Fri 12:09:02 🔄  `running` https://drone.mycompany.io/company/some-service/2506 `My pull request title` https://github.com/company/some-service/pull/23 (AlxndrJhn)
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
