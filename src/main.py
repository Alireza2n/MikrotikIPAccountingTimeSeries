import concurrent
import datetime
import threading

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from decouple import config
from collections import Counter

MIKORITK_DEVICE_IP = config('MIKORITK_DEVICE_IP', cast=str, default='192.168.88.1')
MIKORITK_DEVICE_ACCOUNTING_HTTP_PORT = config('MIKORITK_DEVICE_ACCOUNTING_HTTP_PORT', cast=str, default='80')
MIKORITK_DEVICE_ACCOUNTING_URL = f'http://{MIKORITK_DEVICE_IP}:{MIKORITK_DEVICE_ACCOUNTING_HTTP_PORT}/accounting/ip.cgi'

QUEST_DB_REST_URL = config('QUEST_DB_REST_URL', cast=str, default='http://localhost:9000')
CALL_INTERVAL = config('CALL_INTERVAL', cast=int, default=5)


def create_table() -> None:
    """
    Creates a new table named Traffic
    :return: None
    """
    q = 'CREATE TABLE IF NOT EXISTS traffic ' \
        '(ip string,' \
        'destination string,' \
        'bytes int,' \
        'timestamp timestamp)' \
        'timestamp(timestamp)'
    try:
        r = requests.get(f"{QUEST_DB_REST_URL}/exec", params={'query': q})
        r.raise_for_status()
    except (requests.HTTPError, requests.RequestException) as e:
        print(f'Failed to call DB, {e}')


def gather_and_post_data() -> None:
    """
    Calls Mikrotik accounting URL, parses data then posts
    to QuestDB.
    :return: None
    """
    url = MIKORITK_DEVICE_ACCOUNTING_URL

    try:
        resp = requests.get(url, timeout=2)
        resp.raise_for_status()
    except (requests.HTTPError, requests.RequestException) as e:
        print(f'Failed to gather data from Mikrotik device {MIKORITK_DEVICE_IP}, {e}')
        exit(1)

    state_counter = Counter(success=0, failure=0)

    for item in resp.content.decode().splitlines():
        params = item.split(" ")
        src = params[0]
        dst = params[1]
        _bytes = params[3]
        query = "insert into traffic values(" \
                + f"'{src}'," \
                + f"'{dst}'," \
                + f"{_bytes}," \
                + " systimestamp());"
        try:
            r = requests.get(f"{QUEST_DB_REST_URL}/exec?query=" + query)
            r.raise_for_status()
            state_counter['success'] += 1
        except requests.HTTPError as e:
            print(f'There was an HTTPError, {e}')
            state_counter['failure'] += 1

    print(f'{datetime.datetime.today()} - {state_counter}')


def main() -> None:
    """
    The entrypoint to app
    :return: None
    """
    print('Creating Traffic table if it does not exist.')
    create_table()
    scheduler = BlockingScheduler()
    scheduler.add_job(gather_and_post_data, 'interval', seconds=CALL_INTERVAL)
    scheduler.start()


if __name__ == "__main__":
    main()
