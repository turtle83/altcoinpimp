from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from httplib2 import Http
from datetime import datetime
import json

class Currency:
    def __init__(self, conf):
        self.symbol = conf["symbol"]
        self.algo = conf["algo"]

    def get_difficulty(self):
        """
        Gets the current difficulty of this currency
        """
        pass

    def get_coin_per_day_hash(self):
        """
        How many coins can i get per hash?
        """
        return 1 #DUMMY CALUE

    def __repr__(self):
        return "Currency <%s>" %(self.symbol)

    def __str__(self):
        return "Currency <%s>" %(self.symbol)

class Exchange:
    """
    Class for currency conversions.
    Cache results for future
    """
    def __init__(self):
        self.h = Http() #Initialize here to keep conn pool
        self.cache = {} #Cache obj

    def convert(self, symbol):
        """
        1 of this currency gets me how many BTC?
        """
        cached = self.cache.get(symbol)
        if cached is None or (datetime.now() - cached["updated"]).total_seconds > 300  :
            #I.e. cache doesnt exist or cache is more than 5 min stale
            result = self._convert(symbol)
            self.cache[symbol] = {
                "rate": result,
                "updated": datetime.now()
            }
        else:
            result = cached["rate"]
        return result

    def _convert(self, symbol):
        """
        Choose an exchange, edit symbol if needed...
        """
        if symbol == "BTC":
            return 1.0
        else:
            if True:
                return self._convert_btce(symbol)
            else:
                pass #Not possible, i know, but later we will put more exchanges

    def _convert_btce(self, symbol):
        """
        Do actual lookup at exchange
        """
        resp, cont = self.h.request("https://btc-e.com/api/2/%s_btc/ticker" %(symbol.lower()))
        return float(json.loads(cont)["ticker"]["last"])

class Miner:
    """
    Model representing each individual mining unit
    """
    def __init__(self, config):
        self.config = config
        self.sha256 = float(config.get("sha256", 0))
        self.scrypt = float(config.get("scrypt", 0))

    def get_daily_profit(self, curriencies, exchange):
        result = {}
        for symbol in curriencies.keys():
            #result[symbol] = {}
            currency = curriencies[symbol]
            btc_per_hash = currency.get_coin_per_day_hash() * e.convert(symbol)
            result[symbol] = btc_per_hash * float(self.config.get(currency.algo, 0))
        return result



if "__main__" in __name__ :
    #Load the config
    config = load(open("config.yaml"), Loader=Loader)
    print config
    curriencies = {}
    for coin in config["coins"]:
        curriencies[coin["symbol"]] = Currency(coin)
    print curriencies
    e = Exchange()
    for miner in config["miners"]:
        print miner["name"], Miner(miner).get_daily_profit(curriencies, e)
