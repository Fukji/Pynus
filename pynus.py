import argparse
import csv
import sys
import traceback
from pynus.modes import classes, forums
from pynus.utils import webbrowser

VERSION = 'v0.2.0'
BUILD = '20210518'

browser = None
timeout = 75
debug = False
limit = 7


# Check for positive integer in argument
def positive_int(value):
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError(
                '%s is an invalid positive int value' % value)
        else:
            return value

    except ValueError:
        raise argparse.ArgumentTypeError(
            '%s is an invalid positive int value' % value)


def main():

    # Parse user inputted arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='enable debug mode',
                        action='store_true')
    parser.add_argument('-b', '--browser', default='chrome',
                        help='select custom browser [chrome/firefox]')
    parser.add_argument('-l', '--limit', default=7, type=positive_int,
                        help='limit output (days)')
    parser.add_argument('-t', '--timeout', default=75, type=positive_int,
                        help='set custom timeout (seconds)')
    parser.add_argument('-m', '--mode', default='forum',
                        help='choose mode [forum/class]')
    args = parser.parse_args()

    # Change global variable based on argument value
    global timeout, debug, limit, browser
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
        if args.mode == 'class':
            print('Chrome is currently not supported in this mode, trying to use firefox instead.')
            browser = webbrowser.setup_browser('firefox')
        else:
            browser = webbrowser.setup_browser('chrome')
    elif args.browser == 'firefox':
        browser = webbrowser.setup_browser('firefox')
    elif args.browser == 'edge':
        browser = webbrowser.setup_browser('edge')
    else:
        if args.mode == 'class':
            print('Unrecognized browser, trying to use firefox instead.')
            browser = webbrowser.setup_browser('firefox')
        else:
            print('Unrecognized browser, trying to use chrome instead.')
            browser = webbrowser.setup_browser('chrome')

    # Fetch and check the links
    try:
        if args.mode == 'class':
            classes.standby(browser, args)
        else:
            if args.mode != 'forum':
                print('Invalid mode, running in forum checking mode.')
            newly_replied, links, not_replied = forums.check_link(browser,
                                                                  args)
    except KeyboardInterrupt:
        print('\nProcess terminated without error.')
    except SystemExit:
        sys.exit(0)
    except:
        if debug:
            traceback.print_exc()
        print('Unexpected error occured:', sys.exc_info()[0])

    # Write user's data to csv file
    if args.mode == 'forum':
        forums.write_replied(newly_replied)
        print(f'Checked {len(links)} links.',
              f'Found {len(not_replied)} unreplied/unchecked.')
        forums.print_thread_list(not_replied, limit)

    webbrowser.terminate(browser)


if __name__ == '__main__':
    main()
