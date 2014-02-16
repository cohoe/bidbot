#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2
import argparse
import requests
import time
from datetime import datetime
import ConfigParser
import os
import signal
import re




def main():

    status = "UNKNOWN"

    print "Your maximum bid is: "+ str(bidder.max_) \
            + "\nBids will refresh every " \
            + str(args.timeinterval) + " seconds\n"
#
#    while True:
#        for jersey in bidder.bids:
#            my_bid = bidder.bids[jersey]
#            current_bid_amt = get_current_bid(jersey)
#
#            if current_bid_amt == my_bid:
#                # You are currently the highest bidder
#                status = "WINNING"
#            elif current_bid_amt > bidder.max_:
#                status = "MAXED OUT"
#            elif current_bid_amt > my_bid:
#                #  You are currently not the highest bidder
#                if current_bid_amt < bidder.max_:
#                    new_bid = place_bid(jersey, current_bid_amt)
#                    bidder.update_bid(jersey, new_bid)
#                    my_bid = bidder.bids[jersey]
#                    current_bid_amt = get_current_bid(jersey)
#            elif current_bid_amt < my_bid:
#                #  Something is incorrect
#                print "Something is wrong. Check your numbers (mainly \
#                        your starting bid)."
#
#            elif current_bid_amt > my_bid:
#                status = "LOSING"
#            elif current_bid_amt < my_bid:
#                status = "ERROR"
#
#            print get_timestamp()+"\t Jersey: "+str(jersey)+" Current Bid: " \
#                + str(current_bid_amt)+" ("+str(my_bid)+")\tStatus: "+status
#
#            bidder.bid_status[jersey] = status
#
#        time.sleep(args.timeinterval)
#        print ""


def bid_pool():
    while True:
        print "BEGIN LOOP"
        my_bids = get_bids()
        bid_states = {}
        for bid in my_bids:
            bid_states[bid.status] = None

        if len(bid_states.keys()) is 1 and "MAXED OUT" in bid_states.keys():
            print "Everything is maxed out. Either increase your max bid or leave"
            continue

        if "WINNING" not in bid_states:
            print "You're not winning anything!"
            lowest_jersey_num = min(bidder.bids, key=bidder.bids.get)
            print "Lowest Jersey: "+str(lowest_jersey_num)
            print bidder.bids[lowest_jersey_num]
            my_lowest_bid = get_bid_from_bids(my_bids, lowest_jersey_num)
            new_bid_amt = place_bid(lowest_jersey_num, my_lowest_bid.current_amount)
            my_lowest_bid.update(new_bid_amt)
        print "END LOOP"
        time.sleep(args.timeinterval)
