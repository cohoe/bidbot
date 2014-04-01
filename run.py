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
from bidbot.config import logging
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
        show_auction_status(config)
        return

    # Make a list of bid objects based on the jerseys you want
    for c in config.campaigns:
        my_bids = get_bids_from_string(c.jerseys, c.name)
        c.update_bids(my_bids)

    # Print favorites
    print_favorites(config)


    refresh_bids(config)
    show_bid_report(config)
    print ""
    cont = raw_input("Press Enter to begin bidding or CTRL-C to exit...")

    # Continuously show status and update bids based on your configuration
    while True:
    #    try:
        refresh_bids(config)
        show_bid_report(config)
        win_bid_from_pool(config)
     #   except Exception as e:
            #logging.error("Something bad happened this run. Trying again...")
            #logging.error(e)

        print ""
        sleep(config.time_interval)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, closeout)
    main()
