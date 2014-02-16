#!/usr/bin/env python

import requests
import time
from datetime import datetime
import os
import signal
import re
from time import sleep

import jersey
from config import config
from botlib import *

def main():
    # Header
    print_header()
    print_config(config)

    # Print a status report
    if config.status is True:
        show_auction_status(config.campaign_url)
        return

    # Jersey current amount
    #print get_jersey_current_bid(config.campaign_url, 4)
    my_bids = get_bids(config.jerseys)

    while True:
        my_bids = refresh_bids(config.campaign_url, my_bids, config.max_bid)
        show_bid_report(my_bids)
        my_bids = win_bid_from_pool(my_bids, config)
        sleep(config.time_interval)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, closeout)
    main()
