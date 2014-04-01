class Campaign:
    """
    This is a representation of a specific campaign that you are bidding in.
    """
    def __init__(self, name, url, max_bid, bid_interval, jerseys, favorites):
        self.name = name
        self.url = url
        self.max_bid = max_bid
        self.bid_interval = bid_interval
        self.jerseys = jerseys
        self.favorites = favorites
        self.bids = None

        if self.favorites is not None:
            self.favorites = self.favorites.replace(' ','')
            self.favorites = self.favorites.split(',')
            self.favorites = map(int, self.favorites)
        else:
            self.favorites = []

    def __repr__(self):
        return "<Campaign: "+self.name+">"


    def update_bids(self, bids):
        if self.bids is None:
            self.bids = bids
            self.check_favorites()
        self.bids = bids


    def check_favorites(self):
        if self.favorites is None:
            return
        bid_numbers = set(bid.jersey for bid in self.bids)
        for fav in self.favorites:
            if fav not in bid_numbers:
                print "[ERROR]: Favorite #"+str(fav) + \
                " is not in the available bids for campaign '"+self.name+"'"
                exit(1)

    def get_bid_by_number(self, number):
        for bid in self.bids:
            if bid.jersey is number:
                return bid
        raise Exception("Cannot get_bid_by_number for "+str(number))
