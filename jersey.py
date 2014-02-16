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

