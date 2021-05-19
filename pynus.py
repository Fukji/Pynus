import argparse
import csv
import sys
import traceback
from pynus.modes import classes, forums
from pynus.utils import webbrowser

VERSION = 'v0.2.1'
BUILD = '20210520'


# Check for positive integer in argument
def positive_int(value):
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError(
                '%s is an invalid positive int value.' % value)
        else:
            return value

    except ValueError:
        raise argparse.ArgumentTypeError(
            '%s is an invalid positive int value.' % value)


def main():

    # Parse user inputted arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='enable debug mode',
                        action='store_true')
    parser.add_argument('-b', '--browser', default='chrome',
                        help='select custom browser [chrome/firefox/edge]')
    parser.add_argument('-l', '--limit', default=7, type=positive_int,
                        help='limit output (days)')
    parser.add_argument('-t', '--timeout', default=75, type=positive_int,
                        help='set custom timeout (seconds)')
    parser.add_argument('-m', '--mode', default='forum',
                        help='choose mode [forum/class]')
    args = parser.parse_args()

    # Change global variable based on argument value
    browser = None
    timeout = args.timeout
    debug = args.debug
    limit = args.limit

    # Print version info
    print(f'Pynus {VERSION}', end='')
    if debug:
        print(f' build {BUILD}', end='')
    print()

    # Setup the browser
    args.browser = args.browser.lower()
    args.mode = args.mode.lower()
    if args.browser == 'chrome':
        browser = webbrowser.setup_browser('chrome', debug)
    elif args.browser == 'firefox':
        browser = webbrowser.setup_browser('firefox', debug)
    elif args.browser == 'edge':
        browser = webbrowser.setup_browser('msedge', debug)
    else:
        if args.mode == 'class':
            print('Unrecognized browser, trying to use firefox instead.')
            browser = webbrowser.setup_browser('firefox', debug)
        else:
            print('Unrecognized browser, trying to use chrome instead.')
            browser = webbrowser.setup_browser('chrome', debug)

    # Fetch and check the links
    try:
        if args.mode == 'class':
            classes.standby(browser, args)
        else:
            if args.mode != 'forum':
                print('Invalid mode, running in forum checking mode.')
            forums.check_link(browser, args)
    except KeyboardInterrupt:
        print('\nProcess terminated without error.')
    except SystemExit:
        sys.exit(0)
    except:
        if debug:
            traceback.print_exc()
        print('Unexpected error occured:', sys.exc_info()[0])

    webbrowser.terminate(browser)


if __name__ == '__main__':
    main()
