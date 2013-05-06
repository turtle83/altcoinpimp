from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Currency:
	def __init__(self, conf):
		self.symbol = conf["symbol"]
		pass

	def __repr__(self):
		return "Currency <%s>" %(self.symbol)

	def __str__(self):
		return "Currency <%s>" %(self.symbol)

if "__main__" in __name__ :
	#Load the config
	config = load(open("config.yaml"), Loader=Loader)
	curriencies = {}
	for coin in config["coins"]:
		curriencies[coin["symbol"]] = Currency(coin)
	print curriencies
