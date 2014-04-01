class Bid:
    """
    This is a representation of a bid that you are making for
    a jersey
    """
    def __init__(self, campaign, jersey, current_amount, my_amount):
        self.campaign = campaign
        self.jersey = jersey
        self.current_amount = current_amount
        self.my_amount = my_amount

        self.update_current_amount(my_amount)

        self.favorite = False

    def __repr__(self):
        return "<Bid: {campaign="+self.campaign+",jersey="+str(self.jersey)+",current_amount=" + \
            str(self.current_amount)+",my_amount="+str(self.my_amount) + \
            ",status="+self.status+")}>"

    def update_current_amount(self, new_val, max_bid=0):
        """
        Update the current amount with a new value. Recalculate
        the status to ensure you're winning, losing, maxed, etc
        """
        self.current_amount = new_val

        if self.current_amount >= max_bid:
            self.status = "MAXED OUT"
        elif self.current_amount > self.my_amount:
            self.status = "LOSING"
        elif self.current_amount == self.my_amount:
            self.status = "WINNING"
        elif self.current_amount < self.my_amount:
            self.status = "ERROR"

    def update_my_amount(self, new_val, max_bid=0):
        """
        Update the bid with your new amount. Calls to
        update_current_amount() to recalcuate your status
        """
        self.my_amount = new_val
        self.update_current_amount(new_val, max_bid)
