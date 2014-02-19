#!/usr/bin/env python

import requests
import time
from datetime import datetime
import os
import signal
import re
from time import sleep

from bidbot import jersey
from bidbot.config import config
from bidbot.botlib import *


def main():
    """
    Print out information and update bid status
    """
    # Header
    print_header()
    print_config(config)

    # Print a status report
    if config.status is True:
        show_auction_status(config.campaign_url)
        return

    # Make a list of bid objects based on the jerseys you want
    my_bids = get_bids(config.jerseys)

    # Make sure your favorite is actually something you're bidding on
    if config.favorite:
        bid = get_bid_from_my_bids(my_bids, config.favorite)
        if bid is None:
            print "[ERROR]: Your favorite is not in your list of bids!"
            exit(1)

    print "[DEBUG]: Favorite is "+str(config.favorite)

    # Print an initial status report of your bids
    my_bids = refresh_bids(config.campaign_url, my_bids, config.max_bid)
    show_bid_report(my_bids)
    print ""
    cont = raw_input("Press Enter to begin bidding or CTRL-C to exit...")

    # Continuously show status and update bids based on your configuration
    while True:
        try:
            my_bids = refresh_bids(config.campaign_url, my_bids, config.max_bid)
            show_bid_report(my_bids)
            my_bids = win_bid_from_pool(my_bids, config)
        except:
            print "[ERROR]: Something bad happened this run. Trying again..."

        print ""
        sleep(config.time_interval)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, closeout)
    main()
