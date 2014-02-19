import ConfigParser
from botlib import get_args
import os.path


class Configuration:
    """
    An object representing the configuration state of the program.
    Takes into account both config file and arguments. Args always
    superceed the file
    """
    def __init__(self):
        # Args
        self.args = get_args()
        # File
        self.cp = ConfigParser.RawConfigParser()
        if os.path.isfile(self.args.config):
            self.cp.read(self.args.config)
        else:
            print "[ERROR]: Config file not found!"
            exit(1)

        # There is probably a better way to do this...
        self.name = self.cp.get("bidder", "name")
        if self.args.name:
            self.name = self.args.name
        self.email = self.cp.get("bidder", "email")
        if self.args.email:
            self.email = self.args.email
        self.phone = self.cp.get("bidder", "phone")
        if self.args.phone:
            self.phone = self.args.phone
        self.max_bid = self.cp.getfloat("bidder", "max")
        if self.args.maxbid:
            self.max_bid = self.args.maxbid
        self.jerseys = self.cp.get("bidder", "jerseys")
        if self.args.jerseys:
            self.jerseys = self.args.jerseys
        self.bid_interval = self.cp.getint("bidder", "bid_interval")
        if self.args.bid_interval:
            self.bid_interval = self.args.bid_interval
        self.time_interval = self.cp.getint("bidder", "time_interval")
        if self.args.time_interval is not None:
            self.time_interval = self.args.time_interval
        self.favorite = self.cp.getint("bidder", "favorite")
        if self.args.favorite:
            self.favorite = self.args.favorite

        self.simulate = self.args.simulate
        self.status = self.args.status

        self.campaign_url = self.cp.get("global", "campaign_url")

# Instantiate the Configuration class
config = Configuration()
