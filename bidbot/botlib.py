import argparse
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

from jersey import Jersey
from bid import Bid
import logging


def get_args():
    """
    Parse and establish the arguments we take in on the CLI
    """
    parser = argparse.ArgumentParser(description="Win a hockey jersey \
            from RIT!", epilog="Written by Grant Cohoe \
            (http://grantcohoe.com)")

    # Programmatic Things
    parser.add_argument("--status", dest="status", help="Print status \
                        of bids and exit", action='store_true')
    parser.add_argument("--simulate", dest="simulate", default=False,
                        action='store_true', help="Simulate bidding only")
    parser.add_argument("-d", "--debug", dest="debug", action='store_true',
                        help="Enable debug log messages")
    parser.add_argument("-c", "--config", dest="config", default='config.cfg',
                        help="Specify a config file")
    parser.add_argument("-t", "--time", dest="time_interval", type=int,
                        help="Bid checking interval in seconds \
                        (ex: 1)")

    return parser.parse_args()


def show_auction_status(config):
    """
    Print out a summary report of the current bids on jerseys
    """

    for c in config.campaigns:
        print "[{0}]".format(c.name)
        bidding_url = c.url + "/bidding.php"
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
---------------------------------------------------------------------
RIT Jersey BidBot by Grant Cohoe (RIT '13)

DISCLAIMER: Don't be a dick with this. Wait until the last few 
minutes to use it. I make no guarantees that you'll actually win. You
probably will though. May the odds be ever in your favor!
---------------------------------------------------------------------
'''


def get_timestamp():
    """
    Return the current time in a sane format
    """
    time = datetime.strftime(datetime.now(), '%m-%d %H:%M:%S.%f')
    return re.sub('\d{5}$', '', time)


def get_jersey_current_bid(campaign_url, number):
    """
    Grab the current bid on a given jersey
    """
    bid = requests.get(campaign_url+"/high_bid.php?id="
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


def get_bids_from_string(bid_string, campaign):
    """
    Get a list of bid objects from the config string
    """
    bids = bid_string

    # If specified from the CLI args, then it comes in as a list
    # already and we don't need to split it up. Otherwise, we do
    if not isinstance(bid_string, list):
        bids = bid_string.split(", ")

    bid_objects = []
    for bid in bids:
        # The user is supposed to put a :0 for no bid, but they probably didnt
        if ":" not in bid:
            bid = bid+":0"
        number, my_bid = bid.split(":")
        number = int(number)
        my_bid = float(my_bid)
        bid_obj = Bid(campaign, number, 0, my_bid)
        bid_objects.append(bid_obj)

    return bid_objects


def refresh_bids(config):
    """
    Refresh the current amount of a list of bid objects
    """
    for c in config.campaigns:
        updated_bids = []
        for bid in c.bids:
            current_amount = get_jersey_current_bid(c.url, bid.jersey)
            bid.update_current_amount(current_amount, c.max_bid)
            if bid.jersey in c.favorites:
                bid.favorite = True
            updated_bids.append(bid)
        c.update_bids(updated_bids)


def show_bid_report(config):
    """
    Print a report of the status of your bids
    """
    for c in config.campaigns:
        for bid in c.bids:
            fav_bit = " "
            if bid.favorite is True:
                fav_bit = "*"
            print "{0}    {1:12} #{2:3}    Current: {3} ({4})    Status: {5}".format(get_timestamp(), c.name, str(bid.jersey)+fav_bit, str(bid.current_amount), str(bid.my_amount), bid.status)


def get_bid_from_my_bids(bids, number):
    """
    Get a specific bid from a list of bid objects
    """
    for bid in bids:
        if bid.jersey == number:
            return bid
    raise Exception("Unable to find a bid for "+str(number))


def win_bid_from_pool(config):
    """
    Ensure you are winning at least one bid from a pool
    """
    bid_states = {}
    all_bids = []

    # Get a list of the status's of your bids
    for c in config.campaigns:
        for bid in c.bids:
            bid_states[bid.status] = None
            all_bids.append(bid)

    # All of your jerseys are maxed out.
    if len(bid_states.keys()) is 1 and "MAXED OUT" in bid_states.keys():
        logging.warning("All bids are maxed out. Either increase your max bid or leave")
        return

    # You aren't winning anything. We should fix that.
    if "WINNING" not in bid_states.keys():
        logging.warning("You're not winning anything!")
        losing_bids = get_bids_by_status(all_bids, "LOSING")

        active_bid = get_favorite_bid(config)
        if active_bid is None:
            logging.info("There are no favorites for you")
            logging.debug("There are no favorite bids for you")
            active_bid = get_lowest_bid(losing_bids)
        
        # Update bid object after making a new bid
        logging.debug("Setting active bid to #"+str(active_bid.jersey))
        new_bid = make_bid(active_bid, config)

    else:
        # You are winning at least one! yay!
        logging.warning("You're winning at least one jersey")


def print_config(config):
    """
    Print a string summarizing your bid status
    """
    print "You are: "+config.name+" (Email:"+config.email+"/Phone:"+config.phone+")"
    print "You will check your bids every "+str(config.time_interval) + " seconds"
    print "You are bidding in "+str(len(config.campaigns))+" campaigns:"
    for c in config.campaigns:
        print "\t" + c.name + " (Max: $"+str(c.max_bid)+", Interval: $"+str(c.bid_interval)+")"
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
    # Figure out the campaign
    campaign = None
    for c in config.campaigns:
        if c.name is bid.campaign:
            campaign = c
    if campaign is None:
        raise Exception("Unable to find campaign for bid")

    # Calculate your next bid amount
    bid_amount = bid.current_amount + campaign.bid_interval
    if bid_amount > campaign.max_bid:
        logging.warning("Updated bid is outside of your maximum")
        return bid

    logging.info("Updating bid on jersey #"+str(bid.jersey)+" from " +
                 str(bid.current_amount)+" to "+str(bid_amount) +
                 " (your last bid was "+str(bid.my_amount)+")")

    # This is fake. Don't actually do anything
    if config.simulate is True:
        logging.warning("Simulate mode is on. Not actually bidding. (Would have been %s #%d)" % (bid.campaign, bid.jersey))
        return bid
    try:
        # POST the bid, update the object, update the config file
        post_bid(bid.jersey, bid_amount, config, campaign)
        bid.update_my_amount(bid_amount, campaign.max_bid)
        update_bid_file(bid, config)
    except Exception as e:
        logging.error(e)
        pass

    return bid


def update_bid_file(bid, config):
    """
    Update the config file with new bidding information
    """
    new_amount = bid.current_amount
    jersey = bid.jersey
    logging.debug("Updating file with "+str(jersey)+":"+str(new_amount))

    with open('config.cfg', 'r+') as fh:
        contents = fh.read()
        contents = re.sub(str(bid.jersey)+":[\d\.]+", str(bid.jersey)+":" +
                          str(bid.current_amount), contents)
        fh.seek(0)
        fh.write(contents)
        fh.truncate()


def post_bid(jersey, bid_amount, config, campaign):
    """
    Send off a bid on a specific jersey
    """
    if config.simulate is False:
        payload = {'bidamt': bid_amount, 'player': jersey,
                   'name': config.name, 'email': config.email,
                   'phone': config.phone}

        # The URL to POST to
        submit_url = campaign.url + "/jersey_submit.php"

        # Make the request
        r = requests.post(submit_url, data=payload)
        if r.text.endswith("error"):
            logging.error(r.text)
            raise Exception("Critical POST error")
        elif r.text.endswith("over"):
            logging.error("The auction is over. I'm sorry. We somehow lost.")
            raise Exception("Critical POST error")


def print_favorites(config):
    """
    Print all of the favorite numbers for all campaigns
    """
    for c in config.campaigns:
        fav_string = "None"
        if c.favorites:
            fav_string = '#' + ' #'.join(map(str, c.favorites))

        print "Favorites for '{0}': {1}".format(c.name, fav_string)
    print ""


def get_favorite_bid(config):
    """
    Return the bid to use as your favorite. Goes in numberical order for each
    campaign, then defaults to the first campaign listed
    """

    for c in config.campaigns:
        c_fav_bid = None
        if c.favorites:
            for active_number in c.favorites:
                bid = c.get_bid_by_number(active_number)
                if bid.status is "LOSING":
                    c_fav_bid = bid
                    break

        if c_fav_bid is None:
            continue
        logging.warning("Favorite is "+c.name+" #"+str(c_fav_bid.jersey))
        return c_fav_bid

    # Otherwise there are no favorites left
