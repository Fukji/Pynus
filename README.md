# Pynus
Pynus is a [python](https://wiki.python.org/moin/BeginnersGuide) program for BINUS students to view unreplied forum threads and to join online class automatically.

## Installation
Pynus uses frameworks called Selenium and Webdriver Manager. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install them.

```bash
# If python is set to python 2.x
pip3 install selenium webdriver-manager

# If python is set to python 3.x
pip install selenium webdriver-manager
```

The current version of Pynus only supports [Chrome](https://www.google.com/chrome/), [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [Edge](https://www.microsoft.com/en-us/edge) browser. Before running the program, make sure that compatible browser has been properly installed. To use class mode, please make sure that Zoom has been installed on your system and you are properly logged in.

To use Edge browser, additional dependancy needs to be installed. Use the package manager pip to install them. This step is **optional** if you do not plan on using Edge.

```bash
# If python is set to python 2.x
pip3 install msedge-selenium-tools

# If python is set to python 3.x
pip install msedge-selenium-tools
```

## Usage and Arguments
### Usage
```bash
# If python is set to python 2.x
python3 pynus.py [-h] [-d] [-b BROWSER] [-l LIMIT] [-t TIMEOUT] [-m MODE]

# If python is set to python 3.x
python pynus.py [-h] [-d] [-b BROWSER] [-l LIMIT] [-t TIMEOUT] [-m MODE]
```
### Arguments
| Short | Long        | Default        | Description           |
| ----- | ----------- | -------------- | --------------------- |
| `-h`  | `--help`    |                | Show help             |
| `-d`  | `--debug`   |                | Enable debug mode     |
| `-b`  | `--browser` | `chrome`       | Select custom browser |
| `-l`  | `--limit`   | `7`            | Set custom day limit  |
| `-t`  | `--timeout` | `75`           | Set custom timeout    |
| `-m`  | `--mode`    | `forum`        | Choose mode           |

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://github.com/Fukji/Pynus/blob/main/LICENSE)
