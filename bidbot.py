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


class Bidder:
    """
    This is you. A person who wants a jersey. This class stores
    information about you, jerseys you want, and bids you have.
    """
    def __init__(self, cp):
        self.name = cp.get("bidder", "name")
        self.email = cp.get("bidder", "email")
        self.phone = cp.get("bidder", "phone")
        self.max_ = cp.getfloat("bidder", "max")
        self.jerseys = cp.get("bidder", "jerseys")
        self.jerseys = self.jerseys.split(", ")
        self.bids = {}

    def add_bid(self, num, amount):
        """
        Track a new bid of yours
        """
        self.bids[num] = amount

    def update_bid(self, jersey, amount):
        """
        Update one of your bids
        """
        self.bids[jersey] = amount
        # Print out a new config file
        contents = ""
        with open('bidbot.cfg', 'r+') as fh:
            contents = fh.read()
            contents = re.sub('jerseys = (.*)\n',
                              self.__bid_config_string__(), contents)
            fh.seek(0)
            fh.write(contents)
            fh.truncate()

    def __bid_config_string__(self):
        """
        Generate the line needed to go in the config file
        that will save the state of your bids
        """
        config_line = "jerseys = "
        for jersey in self.bids:
            config_line += str(jersey)+":"+str(self.bids[jersey])+", "

        config_line = re.sub(', $', '', config_line)
        config_line += "\n"

        return config_line

    def __repr__(self):
        return "<Bidder: name='"+self.name+"', max='"+str(self.max_)+"'>"


class Jersey:
    """
    This is a jersey that is being auctioned off.
    """
    def __init__(self, number, name, position, current_amount):
        self.number = number
        self.name = name
        self.position = position
        self.current_amount = current_amount

    def __repr__(self):
        return '{0:20} {1:3}  {2}'.format(self.name, "#"+self.number,
                                          str(self.current_amount))


def show_status():
    """
    Print out a summary report of the current bids on jerseys
    """
    bidding_url = campaign_url + "bidding.php"
    content = urllib2.urlopen(bidding_url).read()
    soup = BeautifulSoup(content)
    jerseys = get_jerseys(soup)
    for j in jerseys:
        print j


def get_jerseys(soup):
    """
    Parse the bidding page to get information on all of the
    jerseys being sold
    """
    jerseys = []

    for jersey in soup.find_all("div", class_='jersey'):
        # Player Number
        player_number = jersey['id']

        # Player Name
        player_name_container = jersey.find("div", class_='jhead')
        player_name = player_name_container.find("div",
                                                 class_='jname').string

        # Player Position
        player_position_container = jersey.find("div", class_='jpos')
        player_position = player_position_container.find("span", class_=
                                                         'jpos-t').string

        # Bid Info
        bid_container = jersey.find("div", class_='jbid')
        bid_action_call = bid_container.find("div", class_=
                                             'jbbutton')['onclick']
        # There's a trailing ; here. not sure if it's
        # going to screw things up later
        bid_current_amount = bid_container.find("span",
                                                class_='jbidamt').string
        # Remove the $ and make it an integer
        bid_current_amount = float(bid_current_amount[1:])

        j = Jersey(player_number, player_name, player_position,
                   bid_current_amount)
        jerseys.append(j)

    return jerseys


def get_args():
    """
    Parse and establish the arguments we take in on the CLI
    """
    parser = argparse.ArgumentParser(description="Win a hockey jersey \
            from RIT!", epilog="Written by Grant Cohoe \
            (http://grantcohoe.com)")
    parser.add_argument("-n", "--name", dest="name", default=bidder.name,
                        help="Specify the name to bid as (ex: 'Grant Cohoe')")
    parser.add_argument("-e", "--email", dest="email", default=bidder.email,
                        help="Specify the email they should contact you at \
                        (ex: 'me@grntm.co')")
    parser.add_argument("-p", "--phone", dest="phone", help="Specify a phone \
                        number to contact you (ex: '330-790-1701')")
    parser.add_argument("-j", "--jersey", dest="jersey", help="The jersey \
                        number you want to bid on", action='append')
    parser.add_argument("-m", "--max", dest="maxbid", default=bidder.max_,
                        help="The maximum amount you want to bid", type=float)
    parser.add_argument("--mybid", dest="mybid", type=float, default=0, help=
                        "Your current bid for use if restarting this program")
    parser.add_argument("-t", "--time", dest="timeinterval", type=int,
                        default=3, help="Bid checking interval in seconds \
                        (ex: 1)")
    parser.add_argument("-b", "--bid", dest="bidinterval", type=int,
                        default=5, help="Amount to increase each bid by")
    parser.add_argument("--status", dest="status", help="Print status \
                        of bids and exit", action='store_true')

    return parser.parse_args()


def get_current_bid(number):
    """
    Grab the current bid on a given jersey
    """
    bid = requests.get(campaign_url+"scripts/high_bid.php?id="
                       + str(number))
    try:
        bid_amt = float(bid.text)
    except ValueError:
        print "RIT returned an error"
        bit_amt = 1

    if bid_amt is 0:
        raise Exception("Jersey value not found")

    return bid_amt


def place_bid(jersey_number, current_amount):
    """
    Place a bid of a given value on a given jersey
    """
    bid_amount = current_amount + args.bidinterval

    print get_timestamp()+"\t Jersey: "+str(jersey_number)+"\t\
            Current Bid: " + str(current_amount)+"\tStatus: Updating \
            to " + str(bid_amount)
    payload = {'bidamt': bid_amount, 'player': jersey_number,
               'name': args.name, 'email': args.email, 'phone': args.phone}

    submit_url = campaign_url + "scripts/jersey_submit.php"

    r = requests.post(submit_url, data=payload)
    if r.text.endswith("error"):
        print r.text
        return current_amount

    return bid_amount


def get_timestamp():
    """
    Return the current time
    """
    return re.sub('\d{5}$', '', str(datetime.now()))


def print_header():
    """
    Print out an informational header
    """
    print '''
RIT Jersey BidBot by Grant Cohoe (RIT '13)

WARNING: Use of this program is subject to your own ethics.
Please don't be a dick about it. Keep the bid interval somewhat
sane (anything less than 2 seconds is totally suspicious). These
jerseys usually go to a good cause, so bid high (interval >= 5).

DISCLAIMER: I make no guarantees that you'll actually win. You probably
will though. May the odds be ever in your favor!
'''


def main():
    """
    The main body of this program. Load in the config file,
    grab the CLI options, and loop across all of time and
    jerseys to ensure you win one.
    """
    # Config file
    config = ConfigParser.RawConfigParser()
    config.read('bidbot.cfg')
    global bidder
    bidder = Bidder(config)

    # Global config
    global campaign_url
    campaign_url = config.get("global", "campaign_url")

    # Arguments
    global args
    args = get_args()

    # Ensure bidder object is correct
    bidder.name = args.name
    bidder.email = args.email
    bidder.phone = args.phone
    bidder.max_ = args.maxbid
    if args.jersey:
        bidder.jerseys = args.jersey

    for jersey in bidder.jerseys:
        num, bid = jersey.split(":")
        bidder.add_bid(int(num), float(bid))

    # Testing

    print_header()
    if args.status:
        show_status()
        return

    status = "UNKNOWN"

    print "Your maximum bid is: "+ str(bidder.max_) + "\n"

    while True:
        for jersey in bidder.bids:
            my_bid = bidder.bids[jersey]
            current_bid_amt = get_current_bid(jersey)

            if current_bid_amt == my_bid:
                # You are currently the highest bidder
                pass
            elif current_bid_amt > my_bid:
                #  You are currently not the highest bidder
                if current_bid_amt < bidder.max_:
                    new_bid = place_bid(jersey, current_bid_amt)
                    bidder.update_bid(jersey, new_bid)
                    my_bid = bidder.bids[jersey]
            elif current_bid_amt < my_bid:
                #  Something is incorrect
                print "Something is wrong. Check your numbers (mainly \
                        your starting bid)."
#
#        # Refresh
            current_bid_amt = get_current_bid(jersey)
#
            if current_bid_amt == my_bid:
                status = "WINNING"
            elif current_bid_amt > bidder.max_:
                status = "MAXED OUT"
            elif current_bid_amt > my_bid:
                status = "LOSING"
            elif current_bid_amt < my_bid:
                status = "ERROR"

            print get_timestamp()+"\t Jersey: "+str(jersey)+" Current Bid: " \
                + str(current_bid_amt)+" ("+str(my_bid)+")\tStatus: "+status
        time.sleep(args.timeinterval)
        print ""


def closeout(signal, frame):
    """
    Close the program
    """
    print '''
WARNING: This program will not factor in bids you make manually. Update
the configuration file with your new bid amount if you do this.
'''
    exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, closeout)
    main()
