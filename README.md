# Pynus
Pynus is a [python](https://wiki.python.org/moin/BeginnersGuide) program for BINUS students to view unreplied forum threads.

## Installation
Pynus uses frameworks called Selenium and Pyderman. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install them.

```bash
# If python is set to python 2.x
pip3 install selenium pyderman

# If python is set to python 3.x
pip install selenium pyderman
```

The current version of Pynus only supports [Chrome](https://www.google.com/chrome/) and [Firefox](https://www.mozilla.org/en-US/firefox/new/) browser. Before running the program, make sure that compatible browser has been properly installed.

## Usage and Arguments
### Usage
```bash
# If python is set to python 2.x
python3 pynus.py [-h] [-d] [-b BROWSER] [-l LIMIT] [-t TIMEOUT]

# If python is set to python 3.x
python pynus.py [-h] [-d] [-b BROWSER] [-l LIMIT] [-t TIMEOUT]
```
### Arguments
| Short | Long        | Default        | Description           |
| ----- | ----------- | -------------- | --------------------- |
| `-h`  | `--help`    |                | Show help             |
| `-d`  | `--debug`   |                | Enable debug mode     |
| `-b`  | `--browser` | `chrome`       | Select custom browser |
| `-l`  | `--limit`   | `7`            | Set custom day limit
| `-t`  | `--timeout` | `75`           | Set custom timeout    |

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://github.com/Fukji/Pynus/blob/main/LICENSE)
