import ConfigParser
from botlib import get_args

class Configuration:
    def __init__(self):
        # File
        self.cp = ConfigParser.RawConfigParser()
        self.cp.read('config.cfg')
        # Args
        self.args = get_args()

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
        self.bid_interval= self.cp.getint("bidder", "bid_interval")
        if self.args.bid_interval:
            self.bid_interval = self.args.bid_interval
        self.time_interval = self.cp.getint("bidder", "time_interval")
        if self.args.time_interval:
            self.time_interval = self.args.time_interval

        self.pool = self.args.pool
        self.simulate = self.args.simulate
        self.status = self.args.status

        self.campaign_url = self.cp.get("global", "campaign_url")

config = Configuration()
