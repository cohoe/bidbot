class Bid:
    def __init__(self, jersey, current_amount, my_amount):
        self.jersey = jersey
        self.current_amount = current_amount
        self.my_amount = my_amount

        self.update_current_amount(my_amount)

    def __repr__(self):
        return "<Bid: {jersey="+str(self.jersey)+",current_amount="+str(self.current_amount)+",my_amount="+str(self.my_amount)+",status="+self.status+")}>"

    def update_current_amount(self, new_val, max_bid=0):
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
        self.my_amount = new_val
        self.update_current_amount(new_val, max_bid)


