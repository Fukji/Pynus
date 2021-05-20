import os
import threading
from time import sleep


def spinner_next():
    global spinner_count
    while True:
        terminal_width = os.get_terminal_size().columns
        if len(spinner_text) + 3 <= terminal_width:
            print(f'{spinner_text: <{terminal_width-2}}{spinner_symbol[spinner_count%4]}',
                  end='\r')
        else:
            text = spinner_text[:terminal_width-6] + '..'
            print(f'{text}  {spinner_symbol[spinner_count%4]}', end='\r')

        spinner_count += 1
        sleep(0.1)

        if spinner_state == 1:
            print(' ' * (terminal_width-1), end='\r')
            while(spinner_state == 1):
                sleep(0.1)

        if spinner_state == 2:
            break


def spinner_pause():
    global spinner_state
    sleep(0.05)
    spinner_state = 1
    sleep(0.11)


def spinner_continue(text='Loading...'):
    global spinner_text, spinner_state
    spinner_text = text
    spinner_state = 0


def spinner_stop():
    global spinner_state
    spinner_pause()
    spinner_state = 2


spinner = threading.Thread(target=spinner_next)
spinner_text = 'Loading..'
spinner_symbol = '|/-\\'
spinner_count = 0
spinner_state = 0
