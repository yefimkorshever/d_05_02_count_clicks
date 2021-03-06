import argparse
import os
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


def create_parser():
    description = '''
    The program uses The Bitly API for
    transforming a long link into a short one
    or getting total clicks of a short link
    '''
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'link',
        metavar='<link>',
        help='long or short link'
    )

    return parser


def is_bitlink(link, token):
    parsed_link = urlparse(link)
    bitlink = f'{parsed_link.hostname}{parsed_link.path}'
    url = 'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}'
    url = url.format(bitlink=bitlink)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.ok


def count_clicks(token, link):
    parsed_link = urlparse(link)
    bitlink = f'{parsed_link.hostname}{parsed_link.path}'
    url = 'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary'
    url = url.format(bitlink=bitlink)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['total_clicks']


def shorten_link(token, link):
    url = 'https://api-ssl.bitly.com/v4/bitlinks/'
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'long_url': link}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['link']


def main():
    load_dotenv()
    token = os.getenv('BITLY_TOKEN')
    parser = create_parser()
    link = parser.parse_args().link

    if is_bitlink(link, token):
        link_handler = count_clicks
        print('Total clicks: ', end='')
    else:
        link_handler = shorten_link
        print('Bitlink: ', end='')

    try:
        print(link_handler(token, link))
    except requests.exceptions.HTTPError as error:
        print(f'Incorrect link "{link}". Error: {error}', file=sys.stderr)


if __name__ == '__main__':
    main()
