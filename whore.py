from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from httplib2 import Http
from datetime import datetime
import json
import operator

h = Http() #Make global

class Currency:
    def __init__(self, conf):
        self.symbol = conf["symbol"]
        self.algo = conf["algo"]
        self.difficultyapi = conf["difficultyapi"]
        self.perblock = conf["perblock"]
        self.difficulty = None
        self.difficultyupdated = None

    def get_difficulty(self):
        if self.difficulty is None or (datetime.now() - self.difficultyupdated).total_seconds() > 60:
            #dont have in cache or cache is > 1 min stale
            self.difficulty = self._get_difficulty()
            self.difficultyupdated = datetime.now()
        return self.difficulty


    def _get_difficulty(self):
        """
        Gets the current difficulty of this currency
        """
        resp, contents = h.request(self.difficultyapi)
        if len(contents) < 100:
            #means its not litecoin
            return float(contents)
        else:
            return float(contents.split("\n")[-2].split(",")[4])

    def get_coin_per_day_hash(self):
        """
        How many coins can i get per hash?
        Understanding based on : http://bitcoin.stackexchange.com/a/4566
        """
        difficulty = self.get_difficulty()
        est_hash_block = difficulty * (2 ** 32) #estimated number of hashes to mine a block
        blocks_per_hash = 1.0 / est_hash_block #Blocks per hash
        reward_per_hash = blocks_per_hash * self.perblock #Reward per hash
        return reward_per_hash * 3600 * 24 # Reward per day going on 1 H/s

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
        self.cache = {} #Cache obj

    def convert(self, symbol):
        """
        1 of this currency gets me how many BTC?
        """
        cached = self.cache.get(symbol)
        if cached is None or (datetime.now() - cached["updated"]).total_seconds() > 300  :
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
        resp, cont = h.request("https://btc-e.com/api/2/%s_btc/ticker" %(symbol.lower()))
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



def formated_print(name, calculation):
    sorted_calc = sorted(calculation.iteritems(), key=operator.itemgetter(1))
    sorted_calc.reverse()
    btc = calculation["BTC"]
    print "=============== %s ==============" %(name)
    for c in sorted_calc:
        print "%s\t%s BTC/day (%s%%)" %(c[0], c[1], (c[1] * 100/btc))
    print "================================="
    

if "__main__" in __name__ :
    #Load the config
    config = load(open("config.yaml"), Loader=Loader)
    #print config
    curriencies = {}
    for coin in config["coins"]:
        curriencies[coin["symbol"]] = Currency(coin)
    #print curriencies
    e = Exchange()
    for miner in config["miners"]:
        formated_print(miner["name"], Miner(miner).get_daily_profit(curriencies, e))
