#!/usr/bin/python3

"""Telepathy cli interface:
    An OSINT toolkit for investigating Telegram chats.
"""

import pandas as pd
import datetime
import requests
import json
import random
import glob
import csv
import os
import getpass
import click
import re
import textwrap
import time

from telethon.errors import SessionPasswordNeededError, ChannelPrivateError
from telethon.tl.types import InputPeerEmpty, PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.messages import GetDialogsRequest
from telethon import TelegramClient, functions, types, utils
from telethon.utils import get_display_name, get_message_id
from telethon.sync import TelegramClient
from colorama import Fore, Back, Style
from alive_progress import alive_bar
from bs4 import BeautifulSoup

__author__ = "Jordan Wildon (@jordanwildon)"
__license__ = "MIT License"
__version__ = "2.0.0"
__maintainer__ = "Jordan Wildon"
__email__ = "j.wildon@pm.me"
__status__ = "Development"

user_agent = [
    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
    #Safari
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) RockMelt/0.9.50.549 Chrome/10.0.648.205 Safari/534.16'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.18 (KHTML, like Gecko) Chrome/11.0.661.0 Safari/534.18'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.19 (KHTML, like Gecko) Chrome/11.0.661.0 Safari/534.19'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.682.0 Safari/534.21'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.1 Safari/534.3'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.461.0 Safari/534.3'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.53 Safari/534.3'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Iron/6.0.475 Safari/534'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.724.100 Safari/534.30'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.6 (KHTML, like Gecko) Chrome/7.0.500.0 Safari/534.6'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7 ChromePlus/1.5.0.0 ChromePlus/1.5.0.0'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7 ChromePlus/1.5.0.0alpha1'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Flock/3.5.2.4599 Chrome/7.0.517.442 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Iron/7.0.520.0 Chrome/7.0.520.0 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Iron/7.0.520.1 Chrome/7.0.520.1 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Iron/7.0.520.1 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) RockMelt/0.8.36.116 Chrome/7.0.517.44 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) RockMelt/0.8.36.128 Chrome/7.0.517.44 Safari/534.7'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.9 (KHTML, like Gecko) Chrome/7.0.531.0 Safari/534.9'
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Iron/0.2.152.0 Safari/13657880.525'
]

@click.command()
@click.option('--target', '-t', default='',
              help='Specifies a chat to investigate.')
@click.option('--comprehensive', '-c', is_flag=True,
              help='Comprehensive scan, includes archiving.')
@click.option('--media', '-m', is_flag=True,
              help='Archives media in the specified chat.')
@click.option('--forwards', '-f', is_flag=True,
              help='Scrapes forwarded messages.')


def cli(target,comprehensive,media,forwards):

    print(Fore.GREEN + """
      ______     __                 __  __
     /_  __/__  / /__  ____  ____ _/ /_/ /_  __  __
      / / / _ \/ / _ \/ __ \/ __ `/ __/ __ \/ / / /
     / / /  __/ /  __/ /_/ / /_/ / /_/ / / / /_/ /
    /_/  \___/_/\___/ .___/\__,_/\__/_/ /_/\__, /
                   /_/                    /____/
    -- An OSINT toolkit for investigating Telegram chats.
    -- Developed by @jordanwildon | Version 2.0.0.
    """)

    print(Style.RESET_ALL)

    # Checking for, or creating Telepathy home directory and credentials file
    telepathy_file = './telepathy_files/'
    try:
        os.makedirs(telepathy_file)
    except FileExistsError:
        pass

    login = telepathy_file + 'login.txt'

    if os.path.isfile(login) == False:
        api_id = input(' Please enter your API ID:\n')
        api_hash = input(" Please enter your API Hash:\n")
        phone_number = input(" Please enter your phone number:\n")
        with open(login, 'w+') as f:
            f.write(api_id + ',' + api_hash + ',' + phone_number)
    else:
        with open(login) as f:
            details = f.read()
            api_id, api_hash, phone_number = details.split(sep=',')

    client = TelegramClient(phone_number, api_id, api_hash)

    # Checking for or creating the directory and filename for the target
    target_clean = target
    alphanumeric = ""
    filetime = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")
    filetime_clean = str(filetime)

    for character in target_clean:
        if character.isalnum():
            alphanumeric += character

    save_directory = telepathy_file + alphanumeric
    try:
        os.makedirs(save_directory)
    except FileExistsError:
        pass

    # Defining default values
    output_print = False
    media_archive = False
    forward_check = False
    forward_verify = False
    last_date = None
    chunk_size = 200

    # Connecting to the Telegram client and defining options
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        client.sign_in(phone_number)
        try:
            client.sign_in(code=input(' Enter code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=getpass.getpass(
                prompt='Password: ', stream=None))

        result = client(GetDialogsRequest(
                        offset_date = last_date,
                        offset_id = 0,
                        offset_peer = InputPeerEmpty(),
                        limit = chunk_size,
                        hash = 0
                        ))
    else:
        if not comprehensive:
            comp_check = False
            print(Fore.GREEN + ' [!] '
                  + Style.RESET_ALL
                  + 'Performing basic scan')
        else:
            print(Fore.GREEN + ' [!] '
                  + Style.RESET_ALL
                  + 'Performing comprehensive scan')

            file_archive = save_directory + '/' + alphanumeric + '_' + filetime_clean + '_archive.csv'
            file_forwards = save_directory + '/edgelists/' + alphanumeric + '_' + filetime_clean + '_edgelist.csv'


            comp_check = True

        if forwards:
            print(Fore.GREEN + ' [!] '
                  + Style.RESET_ALL
                  + 'Forwards will be fetched')

            forward_directory = save_directory + '/edgelists/'

            try:
                os.makedirs(forward_directory)
            except FileExistsError:
                pass

            edgelist_file = forward_directory + '_edgelist.csv'
            forward_check = True


        print('\n' + Fore.GREEN
              + ' [-] '
              + Style.RESET_ALL
              + 'Fetching details for '
              + target
              + '...')

        async def main():

            memberlist_directory = save_directory + '/memberlists'

            try:
                os.makedirs(memberlist_directory)
            except FileExistsError:
                pass

            memberlist_filename = memberlist_directory + '/' + alphanumeric + "_members.csv"

            entity = await client.get_entity(target)
            first_post = 'Not found'


            async for message in client.iter_messages(target, reverse=True):
                year = format(message.date.year, '02d')
                month = format(message.date.month, '02d')
                day = format(message.date.day, '02d')
                hour = format(message.date.hour, '02d')
                minute = format(message.date.minute, '02d')

                date = str(year) + "/" + str(month) + "/" + str(day)
                mtime = str(hour) + ":" + str(minute)
                first_post = date + ", " + mtime + ' UTC'
                break

            if entity.username:
                group_url = 'http://t.me/' + entity.username
                group_username = entity.username
                s = requests.Session()
                s.max_redirects = 10
                s.headers['User-Agent'] = random.choice(user_agent)
                URL = s.get(group_url)
                URL.encoding = 'utf-8'
                html_content = URL.text
                soup = BeautifulSoup(html_content, 'html.parser')
                name = entity.title
                try:
                    group_description = soup.find(
                        'div', {'class': ['tgme_page_description']}).text
                    descript = Fore.GREEN + 'Description: ' + Style.RESET_ALL
                    prefix = descript + ' '
                    preferredWidth = 70
                    wrapper_d = textwrap.TextWrapper(initial_indent = descript,
                                                     width = preferredWidth,
                                                     subsequent_indent = '                  ')
                except:
                    group_description = "None"
                    descript = Fore.GREEN + 'Description: ' + Style.RESET_ALL
                    prefix = descript + ' '
                    preferredWidth = 70
                    wrapper_d = textwrap.TextWrapper(initial_indent = descript,
                                                     width = preferredWidth,
                                                     subsequent_indent = '                  ')
                try:
                    group_participants = soup.find('div', {'class': ['tgme_page_extra']}).text
                    sep = 'members'
                    stripped = group_participants.split(sep, 1)[0]
                    total_participants = stripped.replace(' ','').replace('members','').replace('subscribers','').replace('member','')
                except:
                    total_participants = 'Not found' # could be due to restriction, might need to mention

            else:
                group_url = 'Private group'
                group_username = 'Private group'
                total_participants = 'Not found'
                group_description = 'Not found'

            if entity.broadcast is True:
                chat_type = 'Channel'
            elif entity.megagroup is True:
                chat_type = 'Megagroup'
            elif entity.gigagroup is True:
                chat_type = 'Gigagroup'
            else:
                chat_type = 'Chat'

            if entity.restriction_reason is not None:
                ios_restriction = entity.restriction_reason[0]
                if 1 in entity.restriction_reason:
                    android_restriction = entity.restriction_reason[1]
                    group_status = str(
                        ios_restriction) + ', ' + str(android_restriction)
                else:
                    group_status = str(ios_restriction)
            else:
                group_status = 'None'

            restrict = Fore.GREEN + 'Restrictions:' + Style.RESET_ALL
            prefix = restrict + ' '
            preferredWidth = 70
            wrapper_r = textwrap.TextWrapper(initial_indent = prefix,
                                             width = preferredWidth,
                                             subsequent_indent='                   ')

            if chat_type != 'Channel':
                members = []
                all_participants = []
                all_participants = await client.get_participants(target, limit = 5000)

                for user in all_participants:
                    if user.username:
                        username = user.username
                    else:
                        username = "n/a"
                    if user.first_name:
                        first_name = user.first_name
                    else:
                        first_name = ""
                    if user.last_name:
                        last_name = user.last_name
                    else:
                        last_name = ""
                    if user.phone:
                        phone = user.phone
                    else:
                        phone = "n/a"

                    full_name = (first_name + ' ' + last_name).strip()

                    members_df = pd.DataFrame(members, columns = ['username','full name',
                                                          'user id','phone number',
                                                          'group name'])

                    members.append([username,full_name,user.id,phone,target])

                with open(memberlist_filename,'w+') as save_members:
                    members_df.to_csv(save_members, sep=';')

                found_partipants = len(all_participants)
                found_percentage = int(found_partipants) / int(total_participants) * 100

            if chat_type != 'Channel':
                print('\n' + Fore.GREEN
                      + ' [+] Memberlist fetched'
                      + Style.RESET_ALL)
            else:
                print(Fore.GREEN
                      + '  ┬  Chat details'
                      + Style.RESET_ALL)

            print(Fore.GREEN
                  + '  ├  Title: '
                  + Style.RESET_ALL
                  + str(entity.title))
            print(Fore.GREEN
                  + '  ├  '
                  + Style.RESET_ALL
                  + wrapper_d.fill(group_description))
            print(Fore.GREEN
                  + '  ├  Total participants: '
                  + Style.RESET_ALL
                  + str(total_participants))

            if chat_type != 'Channel':
                print(Fore.GREEN
                      + '  ├  Participants found: '
                      + Style.RESET_ALL
                      + str(found_partipants)
                      + ' (' + str(format(found_percentage,".2f")) + '%)')

            print(Fore.GREEN
                  + '  ├  Username: '
                  + Style.RESET_ALL
                  + str(group_username))
            print(Fore.GREEN
                  + '  ├  URL: '
                  + Style.RESET_ALL
                  + str(group_url))
            print(Fore.GREEN
                  + '  ├  Chat type: '
                  + Style.RESET_ALL
                  + str(chat_type))
            print(Fore.GREEN
                  + '  ├  Chat id: '
                  + Style.RESET_ALL
                  + str(entity.id))
            print(Fore.GREEN
                  + '  ├  Access hash: '
                  + Style.RESET_ALL
                  + str(entity.access_hash))

            if chat_type == 'Channel':
                print(Fore.GREEN
                      + '  ├  Scam: '
                      + Style.RESET_ALL
                      + str(entity.scam))

            print(Fore.GREEN
                  + '  ├  First post date: '
                  + Style.RESET_ALL
                  + str(first_post))

            if chat_type != 'Channel':
                print(Fore.GREEN
                      + '  ├  Memberlist saved to: '
                      + Style.RESET_ALL
                      + memberlist_filename) #tidz in display

            print(Fore.GREEN
                  + '  └  '
                  + Style.RESET_ALL
                  + wrapper_r.fill(group_status)
                  + '\n')

            if forward_check is True and comp_check is False:
                print(Fore.GREEN
                      + ' [-] '
                      + Style.RESET_ALL
                      + 'Calculating number of forwarded messages...')

                forwards_list = []
                forward_count = 0
                private_count = 0
                to_ent = await client.get_entity(target)
                to_title = to_ent.title

                c_forwards = pd.DataFrame(forwards_list,
                                         columns = ['To', 'To_title',
                                                    'From', 'From_ID', 'Username',
                                                    'Timestamp'])


                async for message in client.iter_messages(target):
                    if message.forward is not None:
                        forward_count += 1

                print('\n' + Fore.GREEN
                      + ' [-] '
                      + Style.RESET_ALL
                      + 'Fetching forwarded messages...')

                progress_bar = Fore.GREEN + ' [-] ' + Style.RESET_ALL + 'Progress: '

                with alive_bar(forward_count,
                               dual_line = True,
                               title=progress_bar,
                               length=20) as bar:

                    async for message in client.iter_messages(target):
                        if message.forward is not None:
                            try:
                                f_from_id = message.forward.original_fwd.from_id
                                if f_from_id is not None:
                                    ent = await client.get_entity(f_from_id)
                                    username = ent.username
                                    year = format(message.date.year, '02d')
                                    month = format(message.date.month, '02d')
                                    day = format(message.date.day, '02d')
                                    hour = format(message.date.hour, '02d')
                                    minute = format(message.date.minute, '02d')

                                    date = str(year) + "/" + str(month) + "/" + str(day)
                                    mtime = str(hour) + ":" + str(minute)
                                    timestamp = date + ", " + mtime

                                    substring = "PeerUser"
                                    string = str(f_from_id)
                                    if substring in string:
                                        user_id = re.sub("[^0-9]", "", string)
                                        user_id = await client.get_entity(PeerUser(int(user_id)))
                                        user_id = str(user_id)
                                        result = 'User: ' + str(ent.first_name) + ' / ID: ' + str(user_id.id)
                                    else:
                                        result = str(ent.title)

                                    forwards_df = pd.DataFrame(forwards_list,
                                                      columns = ['To username', 'To name',
                                                                 'From', 'From ID',
                                                                 'From_username', 'Timestamp'])

                                    forwards_list.append([target,to_title,
                                                          result,f_from_id,
                                                          username,timestamp])

                            except Exception as e:
                                if e is ChannelPrivateError:
                                    print('Private channel')
                                continue

                            time.sleep(0.5)
                            bar()

                            with open(edgelist_file,'w+') as save_members:
                                forwards_df.to_csv(save_members, sep=';')

                forwards_found = forwards_df.From.count()
                value_count = forwards_df['From'].value_counts()
                df01 = value_count.rename_axis('unique_values').reset_index(name='counts')

                top_forward_one = df01.iloc[0]['unique_values']
                top_value_one = df01.iloc[0]['counts']
                top_forward_two = df01.iloc[1]['unique_values']
                top_value_two = df01.iloc[1]['counts']
                top_forward_three = df01.iloc[2]['unique_values']
                top_value_three = df01.iloc[2]['counts']
                top_forward_four = df01.iloc[3]['unique_values']
                top_value_four = df01.iloc[3]['counts']
                top_forward_five = df01.iloc[4]['unique_values']
                top_value_five = df01.iloc[4]['counts']

                forward_one = str(top_forward_one) + ', ' + str(top_value_one) + ' forwarded messages'
                forward_two = str(top_forward_two) + ', ' + str(top_value_two) + ' forwarded messages'
                forward_three = str(top_forward_three) + ', ' + str(top_value_three) + ' forwarded messages'
                forward_four = str(top_forward_four) + ', ' + str(top_value_four) + ' forwarded messages'
                forward_five = str(top_forward_five) + ', ' + str(top_value_five) + ' forwarded messages'

                df02 = forwards_df.From.unique()
                unique_forwards = len(df02)

                print('\n' + Fore.GREEN
                      + ' [+] Forward scrape complete'
                      + Style.RESET_ALL)
                print(Fore.GREEN
                      + '  ┬  Statistics'
                      + Style.RESET_ALL)
                print(Fore.GREEN
                      + '  ├  Forwarded messages found: '
                      + Style.RESET_ALL
                      + str(forward_count))
                print(Fore.GREEN
                      + '  ├  Forwards from active public chats: '
                      + Style.RESET_ALL
                      + str(forwards_found))
                print(Fore.GREEN
                      + '  ├  Unique forward sources: '
                      + Style.RESET_ALL
                      + str(unique_forwards))
                print(Fore.GREEN
                      + '  ├  Top forward source 1: '
                      + Style.RESET_ALL
                      + str(forward_one))
                print(Fore.GREEN
                      + '  ├  Top forward source 2: '
                      + Style.RESET_ALL
                      + str(forward_two))
                print(Fore.GREEN
                      + '  ├  Top forward source 3: '
                      + Style.RESET_ALL
                      + str(forward_three))
                print(Fore.GREEN
                      + '  ├  Top forward source 4: '
                      + Style.RESET_ALL
                      + str(forward_four))
                print(Fore.GREEN
                      + '  ├  Top forward source 5: '
                      + Style.RESET_ALL
                      + str(forward_five))
                print(Fore.GREEN
                      + '  └  Edgelist saved to: '
                      + Style.RESET_ALL
                      + edgelist_file + '\n')

            else:

                if comp_check is True:

                    messages = client.iter_messages(target)

                    message_list = []
                    forwards_list = []
                    timecount = []

                    forward_count = 0
                    private_count = 0



                    if media_archive is True:
                        print(Fore.GREEN + ' [!] '
                              + Style.RESET_ALL
                              + 'Media content will be archived')

                    print(Fore.GREEN + ' [!] '
                          + Style.RESET_ALL
                          + 'Calculating number of messages...')

                    message_count = 0

                    async for message in messages:
                        if message is not None:
                            message_count += 1

                    print(Fore.GREEN
                          + ' [-] '
                          + Style.RESET_ALL
                          + 'Fetching message archive...')

                    progress_bar = Fore.GREEN + ' [-] ' + Style.RESET_ALL + 'Progress: '

                    with alive_bar(message_count,
                                   dual_line = True,
                                   title = progress_bar,
                                   length=20) as bar:

                        to_ent = await client.get_entity(target)



                        async for message in client.iter_messages(target,
                                                                  limit = None):
                            if message is not None:
                                try:
                                    c_archive = pd.DataFrame(message_list,
                                                             columns = ['To', 'Message ID',
                                                                         'Display_name', 'ID',
                                                                         'Message_text', 'Timestamp',
                                                                         'Reply', 'Views'])

                                    c_forwards = pd.DataFrame(forwards_list,
                                                              columns = ['To', 'To_title',
                                                                        'From', 'From_ID', 'Username',
                                                                        'Timestamp'])

                                    c_time = pd.DataFrame(timecount,
                                                              columns = ['ID', 'Hour'])

                                    display_name = get_display_name(message.sender)
                                    nameID = message.from_id
                                    year = str(format(message.date.year, '02d'))
                                    month = str(format(message.date.month, '02d'))
                                    day = str(format(message.date.day, '02d'))
                                    hour = str(format(message.date.hour, '02d'))
                                    minute = str(format(message.date.minute, '02d'))

                                    date = year + "-" + month + "-" + day
                                    mtime = hour + ":" + minute
                                    timestamp = date + ', ' + mtime

                                    reply = message.reply_to_msg_id

                                    if message.text is not None:
                                        message_text = '"' + message.text + '"'
                                    else:
                                        message_text = 'none'

                                    if message.forwards is not None:
                                        forwards = int(message.forwards)
                                    else:
                                        forwards = 'None'

                                    if message.views is not None:
                                        views = int(message.views)
                                    else:
                                        views = 'Not found'

                                    message_list.append([target, message.id,
                                                         display_name, nameID,
                                                         message_text, timestamp,
                                                         reply, views])

                                    timecount.append([nameID, hour])

                                    if message.forward is not None:
                                        forward_verify = True
                                        try:
                                            forward_count += 1
                                            to_title = to_ent.title
                                            f_from_id = message.forward.original_fwd.from_id

                                            if f_from_id is not None:
                                                ent = await client.get_entity(f_from_id)
                                                user_string = 'user_id'
                                                channel_string = 'broadcast'

                                                if user_string in str(ent):
                                                    ent_type = 'User'
                                                else:
                                                    if channel_string in str(ent):
                                                        if ent.broadcast is True:
                                                            ent_type = 'Channel'
                                                        elif ent.megagroup is True:
                                                            ent_type = 'Megagroup'
                                                        elif ent.gigagroup is True:
                                                            ent_type = 'Gigagroup'
                                                        else:
                                                            ent_type = 'Chat'
                                                    else:
                                                        continue

                                                if ent.username is not None:
                                                    username = ent.username
                                                else:
                                                    username = 'none'

                                                if ent_type != 'Chat':
                                                    result = str(ent.title)
                                                else:
                                                    result = 'none'

                                                if ent_type == 'User':
                                                    substring_1 = "PeerUser"
                                                    string_1 = str(ent.user_id)
                                                    if substring_1 in string_1:
                                                        user_id = re.sub("[^0-9]", "", string_1)
                                                        user_id = await client.get_entity(PeerUser(int(user_id)))
                                                        user_id = str(user_id)
                                                        result = 'User: ' + str(ent.first_name) + ' / ID: ' + str(user_id)
                                                    else:
                                                        result = str(ent.title)
                                                else:
                                                    result = str(ent.title)


                                                forwards_list.append([target,to_title,
                                                                      result,f_from_id,
                                                                      username,timestamp])



                                            if media_archive == True:
                                                if message.media:
                                                    path = await message.download_media(file = media_directory)
                                                else:
                                                    pass

                                        except ChannelPrivateError:
                                            private_count += 1
                                            continue

                                        except Exception as e:
                                            print("An exception occurred.", e)
                                            continue

                                except Exception as e:
                                    print("An exception occurred.", e)




                            else:
                                message_list.append(['None','None','None',
                                                     'None','None','None',
                                                     'None','None'])
                                pass

                            time.sleep(0.5)
                            bar()


                    with open(file_archive,'w+') as archive_file:
                        c_archive.to_csv(archive_file, sep=';')

                    if forward_check is True:
                        with open(file_forwards, 'w+') as forwards_file:
                            c_forwards.to_csv(forwards_file, sep=';')
                    else:
                        pass

                    messages_found = int(c_archive.To.count())-1

                    if chat_type != 'Channel':
                        pcount = c_archive.Display_name.count()
                        pvalue_count = c_archive['Display_name'].value_counts()
                        df03 = pvalue_count.rename_axis('unique_values').reset_index(name='counts')

                        top_poster_one = str(df03.iloc[0]['unique_values'])
                        top_pvalue_one = df03.iloc[0]['counts']
                        top_poster_two = str(df03.iloc[1]['unique_values'])
                        top_pvalue_two = df03.iloc[1]['counts']
                        top_poster_three = str(df03.iloc[2]['unique_values'])
                        top_pvalue_three = df03.iloc[2]['counts']
                        top_poster_four = str(df03.iloc[3]['unique_values'])
                        top_pvalue_four = df03.iloc[3]['counts']
                        top_poster_five = str(df03.iloc[4]['unique_values'])
                        top_pvalue_five = df03.iloc[4]['counts']

                        poster_one = str(top_poster_one) + ', ' + str(top_pvalue_one) + ' messages'
                        poster_two = str(top_poster_two) + ', ' + str(top_pvalue_two) + ' messages'
                        poster_three = str(top_poster_three) + ', ' + str(top_pvalue_three) + ' messages'
                        poster_four = str(top_poster_four) + ', ' + str(top_pvalue_four) + ' messages'
                        poster_five = str(top_poster_five) + ', ' + str(top_pvalue_five) + ' messages'

                        df04 = c_archive.Display_name.unique()
                        plength = len(df03)

                    else:
                        post_frequency = c_time['Hour'].value_counts()
                        c_t_stats = post_frequency.rename_axis('unique_values').reset_index(name='counts')
                        # one day this'll work out sleeping times
                        #print(c_t_stats)

                    print('\n' + Fore.GREEN
                          + ' [+] Chat archive saved'
                          + Style.RESET_ALL)
                    print(Fore.GREEN
                          + '  ┬  Chat statistics'
                          + Style.RESET_ALL)
                    print(Fore.GREEN
                          + '  ├  Number of messages found: '
                          + Style.RESET_ALL
                          + str(messages_found))
                    if chat_type != 'Channel':
                        print(Fore.GREEN
                              + '  ├  Top poster 1: '
                              + Style.RESET_ALL
                              + str(poster_one))
                        print(Fore.GREEN
                              + '  ├  Top poster 2: '
                              + Style.RESET_ALL
                              + str(poster_two))
                        print(Fore.GREEN
                              + '  ├  Top poster 3: '
                              + Style.RESET_ALL
                              + str(poster_three))
                        print(Fore.GREEN
                              + '  ├  Top poster 4: '
                              + Style.RESET_ALL
                              + str(poster_four))
                        print(Fore.GREEN
                              + '  ├  Top poster 5: '
                              + Style.RESET_ALL
                              + str(poster_five))
                    else:
                        pass
                        # timestamp analysis
                    #    print(Fore.GREEN
                    #          + '  ├  Number of messages: '
                    #          + Style.RESET_ALL
                    #          + str(message_count))

                    print(Fore.GREEN
                          + '  └  Archive saved to: '
                          + Style.RESET_ALL
                          + str(file_archive))


                    if forward_check is True:
                        if forward_count >= 15:
                            forwards_found = c_forwards.From.count()
                            value_count = c_forwards['From'].value_counts()
                            c_f_stats = value_count.rename_axis('unique_values').reset_index(name='counts')

                            top_forward_one = c_f_stats.iloc[0]['unique_values']
                            top_value_one = c_f_stats.iloc[0]['counts']
                            top_forward_two = c_f_stats.iloc[1]['unique_values']
                            top_value_two = c_f_stats.iloc[1]['counts']
                            top_forward_three = c_f_stats.iloc[2]['unique_values']
                            top_value_three = c_f_stats.iloc[2]['counts']
                            top_forward_four = c_f_stats.iloc[3]['unique_values']
                            top_value_four = c_f_stats.iloc[3]['counts']
                            top_forward_five = c_f_stats.iloc[4]['unique_values']
                            top_value_five = c_f_stats.iloc[4]['counts']

                            forward_one = str(top_forward_one) + ', ' + str(top_value_one) + ' forwarded messages'
                            forward_two = str(top_forward_two) + ', ' + str(top_value_two) + ' forwarded messages'
                            forward_three = str(top_forward_three) + ', ' + str(top_value_three) + ' forwarded messages'
                            forward_four = str(top_forward_four) + ', ' + str(top_value_four) + ' forwarded messages'
                            forward_five = str(top_forward_five) + ', ' + str(top_value_five) + ' forwarded messages'

                            c_f_unique = c_forwards.From.unique()
                            unique_forwards = len(c_f_unique)

                            print('\n' + Fore.GREEN
                                  + ' [+] Edgelist saved'
                                  + Style.RESET_ALL)
                            print(Fore.GREEN
                                  + '  ┬  Forwarded message statistics'
                                  + Style.RESET_ALL)
                            print(Fore.GREEN
                                  + '  ├  Forwarded messages found: '
                                  + Style.RESET_ALL
                                  + str(forward_count))
                            print(Fore.GREEN
                                  + '  ├  Forwards from active public chats: '
                                  + Style.RESET_ALL
                                  + str(forwards_found))
                            print(Fore.GREEN
                                  + '  ├  Forwards from private (or now private) chats: '
                                  + Style.RESET_ALL
                                  + str(private_count))
                            print(Fore.GREEN
                                  + '  ├  Unique forward sources: '
                                  + Style.RESET_ALL
                                  + str(unique_forwards))
                            print(Fore.GREEN
                                  + '  ├  Top forward source 1: '
                                  + Style.RESET_ALL
                                  + str(forward_one))
                            print(Fore.GREEN
                                  + '  ├  Top forward source 2: '
                                  + Style.RESET_ALL
                                  + str(forward_two))
                            print(Fore.GREEN
                                  + '  ├  Top forward source 3: '
                                  + Style.RESET_ALL
                                  + str(forward_three))
                            print(Fore.GREEN
                                  + '  ├  Top forward source 4: '
                                  + Style.RESET_ALL
                                  + str(forward_four))
                            print(Fore.GREEN
                                  + '  ├  Top forward source 5: '
                                  + Style.RESET_ALL
                                  + str(forward_five))
                            print(Fore.GREEN
                                  + '  └  Edgelist saved to '
                                  + Style.RESET_ALL
                                  + file_forwards
                                  + '\n') #make edgelist gephi compatible
                        else:
                            print('\n' + Fore.GREEN
                                  + ' [!] Insufficient forwarded messages found'
                                  + Style.RESET_ALL)

                    else:
                        pass


    with client:
        client.loop.run_until_complete(main())

if __name__ == '__main__':
    cli()