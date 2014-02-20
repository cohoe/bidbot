import ConfigParser
from botlib import get_args
import os.path
import logging


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
            logging.error("Config file not found!")
            exit(1)

        self.campaign_url = self.cp.get("global", "campaign_url")

        # Debug Logging
        if self.args.debug:
            logging.basicConfig(format='[%(levelname)s]: %(message)s',
                                level=logging.DEBUG)

            logging.debug("DEBUG IS ACTIVE")
        else:
            logging.basicConfig(format='[%(levelname)s]: %(message)s')

        req_config_items = ["name", "email", "phone", "max_bid", "jerseys",
                            "bid_interval", "time_interval"]
        opt_config_items = ["favorite", "simulate", "status"]
        bidder_head = "bidder"

        file_items = [line[0] for line in self.cp.items(bidder_head)]

        for key in req_config_items + opt_config_items:
            if getattr(self.args, key) is not None:
                setattr(self, key, getattr(self.args, key))
                logging.debug("Key '"+key+"' ATTR")
            elif key in file_items:
                setattr(self, key, self.cp.get(bidder_head, key))
                logging.debug("Key '"+key+"' CONF")
            elif key in opt_config_items:
                setattr(self, key, None)
                logging.debug("Key '"+key+"' OPT")
            else:
                logging.error("Configuration key '"+key+"' not specified" +
                              " in the config file or CLI arguments")
                exit(1)

        config_numbers = ["bid_interval", "time_interval", "max_bid"]
        for key in config_numbers:
            value = getattr(self, key)
            setattr(self, key, float(value))


# Instantiate the Configuration class
config = Configuration()
