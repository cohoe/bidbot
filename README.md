# BidBot
Automatically bid on jerseys auctioned off through the RIT bidding system

# Features
1. Configurable check-in interval
1. Configurable bid interval
1. Bid status
1. Bid on multiple jerseys

# Installation
Just ```git clone``` and make sure you have all the dependencies.

# Configuration
Move the ```bidbot.cfg.example``` to be not an example. Edit the campaign URL if needed and update your information. ```max``` is your maximum bid amount. The ```jerseys``` line indicates which jerseys you want and what bid you currently have on them. 

Examples:
```
jerseys = 27:150, 28:160
```
means that you want jerseys 27 and 28. You have bids of 150 and 160 respectively already on them. If you do not, set this value to 0.

# Usage
```python bidbot.py -h``` will get you help on the available options.
