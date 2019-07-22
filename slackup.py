#!/usr/bin/env python3

"""
This is a simple tool to post status update to a Slack webhook URL
"""

import argparse
import configparser
import datetime
import json
import requests
import getpass
import os
import argparse

def make_json_payload(channel, username, text, emoji):
    payload = {
        'channel': channel,
        'username': username,
        'text': text,
        'emoji': emoji
    }
    return payload

def get_status(date_text):
    ''' Construct a string that contains yesterday and today' status updates
    Returns str
    '''
    print('Slackup. Press Enter button twice to complete daily update')
    yesterday_status = [input('Yesterday:\n')]
    while True:
        line = input()
        if line:
            yesterday_status.append(line)
        else:
            break
    yesterday_text = '\n'.join(yesterday_status)
    
    today_status = [input('Today:\n')]
    while True:
        line = input()
        if line:
            today_status.append(line)
        else:
            break
    today_text = '\n'.join(today_status)
    
    status_text = ''.join(['*Slackup ', date_text, '*', '\n',
        '*Yesterday:*\n', yesterday_text, '\n', '*Today:*\n', today_text])
    return status_text

def get_today_str_iso8601():
    ''' Obtain current date in ISO8601 format, without the hyphens,
        e.g., 20190717.
    Returns str
    '''
    return datetime.datetime.today().isoformat()[:10]

def get_username():
    ''' Obtain the current username under which the script is run
    Returns str
    '''
    return getpass.getuser()

def post_to_webhook(url, payload):
    r = requests.post(url, json=payload)
    return r.status_code

def do_slackup(config_file_path):
    channel, webhook_url, username = load_configuration(config_file_path)
    emoji = ':startrek:'
    text = get_status(get_today_str_iso8601())
    payload = make_json_payload(channel, username, text, emoji)
    status = post_to_webhook(webhook_url, payload)
    print('HTTP response status: ', status)
    #print('webhook_url: ', webhook_url)
    #print('payload: ', payload)

def load_configuration(config_file_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)
        webhook_url = config.get('DEFAULT', 'webhook_url')
        username = config.get('DEFAULT', 'username')
        channel = config.get('DEFAULT', 'channel')
        if username != get_username():
            raise Exception('username mismatch. In config file: ' + username
                            + '; in system: ' + get_username())

        return channel, webhook_url, username
    except Exception as ex:
        print('ERROR: Invalid configuration. Check', config_file_path,
              'settings')
        print(ex)
        exit(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Slackup: send yesterday and today\'s status update to Slack.\n'
                    '\n'
                    '  Before first use, edit .config to add appropriate values for '
                    'the webhook URL, username, and Slack channel name.\n'
                    '  At prompt, enter status update for yesterday and today.'
                    '  It takes multiline input for status update. Press Enter twice '
                    'to complete input.\n'
                    '  Example: \n\n'
                    '  python3 slackup.py\n'
                    '  Slackup. Press Enter button twice to complete daily update\n'
                    '  Yesterday:\n'
                    '  y: item 1\n'
                    '  y: item 2\n'
                    '\n'
                    '  Today:\n'
                    '  t: item 3\n'
                    '  t: item 4\n'
                    '\n'
                    '  HTTP response status:  200\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.parse_args()

    config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.config')
    do_slackup(config_file_path) 

