# Pynus
Pynus is a [python3](https://wiki.python.org/moin/BeginnersGuide) program for BINUS students to view their unfinished assignments & unreplied forums.

## Installation
Pynus uses a portable framework called Selenium. Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install Selenium.

```bash
pip3 install selenium
```
The current version of Pynus only supports web browsers listed below. Before running the program, make sure that compatible browser and the respective driver has been properly installed and is in your PATH.
Web Browser   | Driver
------------- | -------------
[Chrome](https://www.google.com/chrome/)        | [ChromeDriver](https://chromedriver.chromium.org/)
[Firefox](https://www.mozilla.org/en-US/firefox/new/)       | [GeckoDriver](https://github.com/mozilla/geckodriver/releases)

## Usage

```bash
python3 pynus.py [-h] [-d] [-b BROWSER] [-t TIMEOUT]
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://github.com/Fukji/Pynus/blob/main/license.txt)
