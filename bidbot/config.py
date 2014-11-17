import ConfigParser
from botlib import get_args
import os.path
import logging
from campaign import Campaign


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


        # Debug Logging
        if self.args.debug:
            logging.basicConfig(format='[%(levelname)s]: %(message)s',
                                level=logging.DEBUG)
            logging.debug("DEBUG IS ACTIVE")
        else:
            logging.basicConfig(format='[%(levelname)s]: %(message)s')

        # Set up lists of config keys
        global_req_items = ["name", "email", "phone", "time_interval"]
        global_opt_items = ["simulate", "status"]
        campaign_req_items = ["campaign_url", "max_bid", "bid_interval",
                              "jerseys"]
        campaign_opt_items = ["favorites"]

        self.campaigns = []
        for section in self.cp.sections():
            if self.cp.has_option(section, "campaign_url"):
                for item in campaign_req_items:
                    # Check that all required keys are there
                    if self.cp.has_option(section, item) is False:
                        print "Key '"+item+"' is missing from section '" + \
                              section+"'"
                        exit(1)

                    # Then assign them useful names
                    url = self.cp.get(section, "campaign_url")
                    max_bid = self.cp.getint(section, "max_bid")
                    bid_interval = self.cp.getint(section, "bid_interval")
                    jerseys = self.cp.get(section, "jerseys")

                # These things are optional, so it doesn't matter
                try:
                    favorites = self.cp.get(section, "favorites")
                except ConfigParser.NoOptionError as e:
                    favorites = None

                c = Campaign(section, url, max_bid, bid_interval, jerseys, 
                             favorites)
                self.campaigns.append(c)

        # Set the config object attributes for optional items
        for item in global_opt_items:
            if getattr(self.args, item) is not None:
                setattr(self, item, getattr(self.args, item))

        # Set the config object attributes for required items.
        # Either from config file or from CLI
        for item in global_req_items:
            try:
                arg_value = getattr(self.args, item)
                if arg_value is None:
                    raise AttributeError
                # Do it from CLI args
                setattr(self, item, getattr(self.args, item))
            except AttributeError:
                # No argument was given. Do it from file.
                setattr(self, item, self.cp.get("global", item))
                

#        file_items = [line[0] for line in self.cp.items(bidder_head)]

#        for key in req_config_items + opt_config_items:
#            if getattr(self.args, key) is not None:
#                setattr(self, key, getattr(self.args, key))
#                logging.debug("Key '"+key+"' ATTR")
#            elif key in file_items:
#                setattr(self, key, self.cp.get(bidder_head, key))
#                logging.debug("Key '"+key+"' CONF")
#            elif key in opt_config_items:
#                setattr(self, key, None)
#                logging.debug("Key '"+key+"' OPT")
#            else:
#                logging.error("Configuration key '"+key+"' not specified" +
#                              " in the config file or CLI arguments")
#                exit(1)

#        config_numbers = ["bid_interval", "time_interval", "max_bid"]
#        for key in config_numbers:
#            value = getattr(self, key)
#            setattr(self, key, float(value))


# Instantiate the Configuration class
config = Configuration()
