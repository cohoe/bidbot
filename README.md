# BidBot
Automatically bid on jerseys auctioned off through the RIT bidding system

# Features
1. Multiple campaigns at once
1. Configurable check-in and bid amount intervals
1. Auction status report
1. Bid on a pool of jerseys
1. Bid to the max on a series of favorite jersey

# Screenshot
![Demo](/screenshot.png "Screenshot of current bid status")

# Installation
Just ```git clone``` and make sure you have all the dependencies.

# Configuration
Move the ```config.cfg.example``` to be not an example. Edit the campaign URL if needed and update your information. ```max``` is your maximum bid amount. The ```jerseys``` line indicates which jerseys you want and what bid you currently have on them. ```favorites``` are an optional list that can specify your favorite jerseys that you'll go to the max bid for (in order).

Examples:
```
jerseys = 27:150, 28:160
favorite = 28, 27
```
This means that you want jerseys 27 and 28. You have bids of 150 and 160 respectively already on them. If you do not, set this value to 0. You will bid to your maximum amount for jersey 28 before bidding on 27.

# Usage
```python run.py -h``` will get you help on the available options.

# Future Plans
1. ncurses-like screen printing for more sane viewing
1. Live status view highlighting recent increases
1. Historical graphs

