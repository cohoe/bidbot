import argparse
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

from jersey import Jersey
from bid import Bid


def get_args():
    """
    Parse and establish the arguments we take in on the CLI
    """
    parser = argparse.ArgumentParser(description="Win a hockey jersey \
            from RIT!", epilog="Written by Grant Cohoe \
            (http://grantcohoe.com)")
    parser.add_argument("-n", "--name", dest="name",
                        help="Specify the name to bid as (ex: 'Grant Cohoe')")
    parser.add_argument("-e", "--email", dest="email",
                        help="Specify the email they should contact you at \
                        (ex: 'me@grntm.co')")
    parser.add_argument("-p", "--phone", dest="phone", help="Specify a phone \
                        number to contact you (ex: '330-790-1701')")
    parser.add_argument("-j", "--jersey", dest="jerseys", help="The jersey \
                        number you want to bid on", action='append')
    parser.add_argument("-m", "--max", dest="maxbid",
                        help="The maximum amount you want to bid", type=float)
    parser.add_argument("--mybid", dest="mybid", type=float, help=
                        "Your current bid for use if restarting this program")
    parser.add_argument("-t", "--time", dest="time_interval", type=int,
                        help="Bid checking interval in seconds \
                        (ex: 1)")
    parser.add_argument("-b", "--bid", dest="bid_interval", type=int,
                        help="Amount to increase each bid by")
    parser.add_argument("--status", dest="status", help="Print status \
                        of bids and exit", action='store_true')
    parser.add_argument("--simulate", dest="simulate", default=False,
                        action='store_true', help="Simulate bidding only")
    parser.add_argument("-f", "--favorite", dest="favorite", type=int,
                        help="Choose a jersey to go to the max for")
    parser.add_argument("-c", "--config", dest="config", default='config.cfg',
                        help="Specify a config file")

    return parser.parse_args()


def show_auction_status(campaign_url):
    """
    Print out a summary report of the current bids on jerseys
    """

    bidding_url = campaign_url + "bidding.php"
    content = urllib2.urlopen(bidding_url).read()
    soup = BeautifulSoup(content)
    jerseys = get_auctioned_jerseys(soup)
    for j in jerseys:
        print j


def get_auctioned_jerseys(soup):
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


def get_timestamp():
    """
    Return the current time in a sane format
    """
    return re.sub('\d{5}$', '', str(datetime.now()))


def get_jersey_current_bid(campaign_url, number):
    """
    Grab the current bid on a given jersey
    """
    bid = requests.get(campaign_url+"scripts/high_bid.php?id="
                       + str(number))
    try:
        bid_amt = float(bid.text)
    except ValueError:
        print "RIT returned an error when getting the current bid amount"
        bid_amt = 0

    if bid_amt is 0:
        raise Exception("Jersey value not found")

    return bid_amt


def closeout(signal, frame):
    """
    Exit the program
    """
    print "\nSee ya! You suck!"
    exit()


def get_bids(bid_string):
    """
    Get a list of bid objects from the config string
    """
    bids = bid_string.split(", ")
    bid_objects = []
    for bid in bids:
        number, my_bid = bid.split(":")
        number = int(number)
        my_bid = float(my_bid)
        bid_obj = Bid(number, 0, my_bid)
        bid_objects.append(bid_obj)

    return bid_objects


def refresh_bids(campaign_url, bids, max_bid):
    """
    Refresh the current amount of a list of bid objects
    """
    updated_bids = []
    for bid in bids:
        current_amount = get_jersey_current_bid(campaign_url, bid.jersey)
        bid.update_current_amount(current_amount, max_bid)
        updated_bids.append(bid)

    return updated_bids


def show_bid_report(bids):
    """
    Print a report of the status of your bids
    """
    for bid in bids:
        print get_timestamp()+"\t Jersey: "+str(bid.jersey)+"\t Current Bid: "\
            + str(bid.current_amount)+" ("+str(bid.my_amount)+")\tStatus: " \
            + bid.status


def get_bid_from_my_bids(bids, number):
    """
    Get a specific bid from a list of bid objects
    """
    for bid in bids:
        if bid.jersey == number:
            return bid
    raise Exception("Unable to find a bid for "+str(number))


def win_bid_from_pool(my_bids, config):
    """
    Ensure you are winning at least one bid from a pool
    """
    bid_states = {}

    # Get a list of the status's of your bids
    for bid in my_bids:
        bid_states[bid.status] = None

    # All of your jerseys are maxed out.
    if len(bid_states.keys()) is 1 and "MAXED OUT" in bid_states.keys():
        print "All bids are maxed out. Either increase your max bid or leave"
        return my_bids

    # You aren't winning anything. We should fix that.
    if "WINNING" not in bid_states.keys():
        print "[INFO]: You're not winning anything!"
        losing_bids = get_bids_by_status(my_bids, "LOSING")
        # If you have a favorite, we will default to that until it is maxed out
        if config.favorite:
            try:
                active_bid = get_bid_from_my_bids(losing_bids, config.favorite)
            except Exception:
                # Your favorite jersey is maxed out
                print "[WARNING]: Favorite jersey ("+str(config.favorite) + \
                      ") is maxed out. Picking lowest remaining."
                active_bid = get_lowest_bid(losing_bids)
        else:
            # You have no favorite
            active_bid = get_lowest_bid(losing_bids)

        # Update bid object after making a new bid
        print "[DEBUG]: Setting active bid to #"+str(active_bid.jersey)
        new_bid = make_bid(active_bid, config)

        # Add it back into the list of your active bids
        new_bids = []
        for bid in my_bids:
            if bid.jersey == new_bid.jersey:
                new_bids.append(new_bid)
            else:
                new_bids.append(bid)
    else:
        # You are winning at least one! yay!
        print "[INFO]: You're winning at least one jersey"

    return my_bids


def print_config(config):
    """
    Print a string summarizing your bid status
    """
    print "You are: "+config.name+" ("+config.email+")"
    print "Your maximum bid is: "+str(config.max_bid)
    print "You will check your bids every "+str(config.time_interval) + \
        " seconds and re-bid at $"+str(config.bid_interval)+" intervals"
    print ""


def get_bids_by_status(bids, state):
    """
    Get a list of your bids with a given status
    """
    ret_bids = []
    for bid in bids:
        if bid.status == state:
            ret_bids.append(bid)

    return ret_bids


def get_lowest_bid(my_bids):
    """
    From a list of bids, get the lowest valued one
    """
    val = min(bid.current_amount for bid in my_bids)
    for bid in my_bids:
        if bid.current_amount == val:
            return bid


def make_bid(bid, config):
    """
    Make a bid on a jersey
    """
    # Calculate your next bid amount
    bid_amount = bid.current_amount + config.bid_interval
    if bid_amount > config.max_bid:
        print "[WARNING]: Updated bid is outside of your maximum"
        return bid

    print "[INFO]: Updating bid on jersey #"+str(bid.jersey)+" from " + \
        str(bid.current_amount)+" to "+str(bid_amount) + \
        " (your last bid was "+str(bid.my_amount)+")"

    # This is fake. Don't actually do anything
    if config.simulate is True:
        print "[WARNING] Simulate mode is on. Not actually bidding on anything"
        return bid
    try:
        # POST the bid, update the object, update the config file
        post_bid(bid.jersey, bid_amount, config)
        bid.update_my_amount(bid_amount, config.max_bid)
        update_bid_file(bid, config)
    except Exception:
        # Something didn't update. We'll catch it on the next run
        pass

    return bid


def update_bid_file(bid, config):
    """
    Update the config file with new bidding information
    """
    new_amount = bid.current_amount
    jersey = bid.jersey
    print "[DEBUG]: Updating file with "+str(jersey)+":"+str(new_amount)

    with open('config.cfg', 'r+') as fh:
        contents = fh.read()
        contents = re.sub(str(bid.jersey)+":[\d\.]+", str(bid.jersey)+":" +
                          str(bid.current_amount), contents)
        fh.seek(0)
        fh.write(contents)
        fh.truncate()


def post_bid(jersey, bid_amount, config):
    """
    Send off a bid on a specific jersey
    """
    if config.simulate is False:
        payload = {'bidamt': bid_amount, 'player': jersey,
                   'name': config.name, 'email': config.email,
                   'phone': config.phone}

        # The URL to POST to
        submit_url = config.campaign_url + "scripts/jersey_submit.php"

        # Make the request
        r = requests.post(submit_url, data=payload)
        if r.text.endswith("error"):
            print "[ERROR]: " + r.text
            raise Exception("Critical POST error")
