# Import system for debugging controls
import sys

# Import necessary libraries for calculation
import math
import numpy as np
import time

# Import Candlestick charting library with desired functionality
from mpl_finance import candlestick_ohlc
import mpl_finance as mpf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import pandas as pd


# Class for the individual trader
class trader(object):
	def __init__(self, ID):

		# Every trader will have their own ID
		self.id = ID

		# Every trader starts with $100K
		self.account_balance = np.random.randint(1000,1000000, size = None)
		self.account_equity = self.account_balance
		self.account_balance_history = []
		self.account_equity_history = []

		# Every trader will have their own max number of trades
		self.max_trades = np.random.randint(1,5, size = None)
		self.current_num_of_trades = 0
		self.total_num_of_trades = 0

		# If a trader breaches the equity stop they will no longer be allowed to trade. 
		self.equitystop = 100
		self.stop_trading = False

		# Risk reward is the ratio between how much they risk and their expected reward
		self.riskreward = np.random.randint(1,5, size = None)
		self.stoplength = np.random.randint(10,100, size = None)

		# Every trader will have their own risk appetite
		self.risk_appetite = self.calc_risk_appetite()

		# Entry positions x Entry Volumes x TPs x SLs
		self.entry_prices = np.zeros(self.max_trades)
		self.entry_volumes = np.zeros(self.max_trades)
		self.tps = np.zeros(self.max_trades)
		self.sls = np.zeros(self.max_trades)

		# traders volume
		self.volume = self.calculate_volume()

		# Inventory is total number of volumes "-3" means they are net short 3 contracts "5" means net long 5
		self.inventory = 0


	def calc_risk_appetite(self):
		risk_multiple = np.random.randint(1,20, size = None)
		risk_percent = risk_multiple * 0.01
		appetite = self.account_equity * risk_percent
		return appetite

	def isequitybreached(self, current_price):
		breached = False
		profit = self.calculate_overall_profit(current_price)
		self.account_equity = self.account_balance + profit
		if self.account_equity < self.equitystop:
			breached = True
		return breached

	def choose_action(self):
		action_space = np.random.randint(1,100, size = None)
		if action_space < 25:
			action = "buy"
		if action_space >= 25 and action_space < 50:
			action = "sell"
		if action_space >= 50 and action_space < 75:
			action = "do nothing"
		if action_space >= 75:
			action = "close all"

		return action

	def calculate_average_entry_price(self):
		cumulative_price = 0
		for i in range(self.max_trades):
			cumulative_price += self.entry_prices[i]
		average = cumulative_price/self.max_trades
		average = round(average,2)
		return average

	def calculate_inventory(self):
		inventory = 0
		for i in range(self.max_trades):
			inventory += self.entry_volumes[i]
		return inventory

	def find_first_empty(self):
		index = 0
		for i in range(self.max_trades):
			if self.entry_prices[i] == 0:
				index = i
				break
		return index

	def calculate_volume(self):
		risk_per_point = self.risk_appetite/self.stoplength
		risk_per_point = round(risk_per_point,2)
		# print(risk_per_point, "Contracts")
		return risk_per_point

	def calculate_overall_profit(self, current_price):
		overall_profit = 0
		# inventory = self.calculate_inventory()
		# average_entry_price = self.calculate_average_entry_price()
		for i in range(self.max_trades):
			position_profit = self.calculate_position_profit(current_price,i)
			overall_profit += position_profit
		return overall_profit

	def calculate_position_profit(self, current_price, position):
		position_profit = (current_price - self.entry_prices[position]) * self.entry_volumes[position]
		return position_profit



# Class for the actual market environment itself
class market(object):
	def __init__(self):
		# In this environment all traders will be trading against eachother in that their orders will affect the market
		# It will take 10 contracts to move the market price 1 point so if a trader buys 25 contracts the market will move 2.5 points
		# 1 contract will equate to $1 per point. 25 contracts will be $25 per point (inventory * (current price - Entry Price))

		# Overall Tick Count (Tick only incremented when buy, sell or close order is placed)
		self.tick_count = 0
		self.max_ticks = 50000

		# Ticks per Candle
		self.ticks_per_candle = 200

		# Minutes per Candle
		self.minutes_per_candle = 5

		# Overall candles
		self.current_candles = []
		self.candle_position = 0

		# Previous Candles
		self.previous_open = []
		self.previous_high = []
		self.previous_low = []
		self.previous_close = []
		self.previous_volume = []

		# How many contracts it takes to move the market 1 point
		self.contract_size = 100

		# The difference between the bid and ask
		self.spread = 0.02

		# The prices in which traders will LONG and SHORT the market
		self.bid = 5000.0
		self.ask = self.bid + self.spread

		# Current OHLC
		self.open = self.bid
		self.high = self.bid
		self.low = self.bid
		self.close = self.bid
		self.volume = 0

		self.tickopen = []
		self.tickhigh = []
		self.ticklow = []
		self.tickclose = []
		self.tickvolume = []

		self.client_tp_sl_script = []


		# Keep track of overall net market volume
		self.market_net_volume = 0
		self.market_maker_revenue = 0
		self.market_maker_revenue_history = []
		self.market_maker_transaction = 0
		self.market_maker_transaction_list = []

		# initialize traders
		self.num_of_traders = 50
		self.trader = []
		for i in range(self.num_of_traders):
			self.trader.append(trader(ID = i))

		# Initialize matplotlib chart

		self.fig = plt.figure(constrained_layout = True)
		self.gspec = self.fig.add_gridspec(ncols = 3, nrows = 3)

		self.ax0 = self.fig.add_subplot(self.gspec[0:2, :])
		self.ax1 = self.fig.add_subplot(self.gspec[2, :])

		self.ax0.set_ylabel('Price')
		self.ax1.set_ylabel('volume')
		plt.title('Virtual CFD Market Simulator')

		self.plot_shown = False
		# plt.ion()
		

		# update the market price based on volume from traders
	def update_price(self, volume):
		self.market_net_volume += volume
		self.volume += abs(volume)
		self.bid += (volume/self.contract_size)
		self.bid = round(self.bid,2)
		self.ask = self.bid + self.spread
		self.ask = round(self.ask,2)
		self.close = self.bid

		self.update_candle()

		self.tickopen.append(self.open)
		self.tickhigh.append(self.high)
		self.ticklow.append(self.low)
		self.tickclose.append(self.close)
		self.tickvolume.append(self.volume)

		if self.tick_count % self.ticks_per_candle == 0:
			self.create_new_candle()

		print("processing Tick #", self.tick_count)
		self.tick_count += 1



	def update_candle(self):
		if self.close > self.high:
			self.high = self.close
		if self.close < self.low:
			self.low = self.close

	def create_new_candle(self):
		self.open = self.close
		self.high = self.close
		self.low = self.close
		self.close = self.close
		self.volume = 0

	def archive_candle(self, i):
		self.market_maker_revenue_history.append(self.market_maker_revenue)
		self.current_candles.append(self.candle_position)
		self.previous_open.append(round(self.tickopen[i], 2))
		self.previous_high.append(round(self.tickhigh[i], 2))
		self.previous_low.append(round(self.ticklow[i], 2))
		self.previous_close.append(round(self.tickclose[i], 2))
		self.previous_volume.append(round(self.tickvolume[i], 2))
		self.candle_position += 1
		print("candle count: ", self.candle_position)

	def update_archive_candles(self, i):
		self.current_candles.append(self.candle_position)
		self.previous_open.append(round(self.tickopen[i], 2))
		self.previous_high.append(round(self.tickhigh[i], 2))
		self.previous_low.append(round(self.ticklow[i], 2))
		self.previous_close.append(round(self.tickclose[i], 2))
		self.previous_volume.append(round(self.tickvolume[i], 2))
		self.candle_position += 1

	def clear_updated_archive_candles(self, i):
		del(self.current_candles[-1])
		del(self.previous_open[-1])
		del(self.previous_high[-1])
		del(self.previous_low[-1])
		del(self.previous_close[-1])
		del(self.previous_volume[-1])
		self.candle_position -= 1

	def print_candles(self, i):
		print("Tick #", i, self.client_tp_sl_script[i])


		if i > 0 and i % self.ticks_per_candle == 0:
			self.archive_candle(i)

		self.update_archive_candles(i)

		data = (self.current_candles, self.previous_open, self.previous_high, self.previous_low, self.previous_close, self.previous_volume)
		dataframe = pd.DataFrame(data)
		dataframe = pd.DataFrame.transpose(dataframe)
		dataframe.columns = ['candle','open','high','low','close','volume']

		volumeframe = dataframe["volume"]
		# print(dataframe)

		self.ax0.clear()
		plt.cla()

		self.ax0.set_ylabel('Price')
		self.ax1.set_ylabel('volume')
		plt.title('Virtual CFD Market Simulator')

		candlestick_ohlc(self.ax0, dataframe.values, width = 0.6, colorup = 'green', colordown = 'red', alpha = 0.8)
		plt.bar(self.current_candles, volumeframe.values, width = 0.6, bottom = 0.0, color = 'black')

		self.clear_updated_archive_candles(i)
		


	def find_most_profitable(self):
		trader = 0
		max_profit = 0
		for i in range(self.num_of_traders):
			if self.trader[i].account_balance > max_profit:
				trader = i
				max_profit = self.trader[i].account_balance

		# Print the traders stats & info
		print("")
		print("Most profitable trader ID# ", trader)
		print("Profit :", round(max_profit - 100000, 2))
		# print(self.trader[trader].account_balance_history)
		print("Risk appetite: ", self.trader[trader].risk_appetite)
		print("Volume: ", self.trader[trader].volume)
		print("Total number of trades: ",self.trader[trader].total_num_of_trades)
		print("Risk to Reward: ", self.trader[trader].riskreward)

		print("Market Maker revenue: ", self.market_maker_revenue)
		print("")


	# Main Loop

	def start(self):
		self.create_new_candle()
		contin = 0
		while self.tick_count < self.max_ticks:
			# Loop through all traders

			for i in range(self.num_of_traders):

				# Check if they're able to trade, if equity stop is breached close all positions
				if self.trader[i].isequitybreached(self.close) == True and self.trader[i].stop_trading == False:
					# print("Trader ID#", i , "Has Breached Max Drawdown")
					for position in range(self.trader[i].max_trades):
						self.update_price(self.trader[i].entry_volumes[position]* -1)
						profit = self.trader[i].calculate_position_profit(self.close, position)
						volume = self.trader[i].entry_volumes[position]
						self.trader[i].account_balance += profit
						self.trader[i].account_balance = round(self.trader[i].account_balance, 2)
						self.trader[i].account_balance_history.append(self.trader[i].account_balance)
						self.market_maker_revenue += profit * -1
						self.market_maker_revenue = round(self.market_maker_revenue, 2)
						# Liquidate their entire inventory
						self.trader[i].entry_volumes[position] = 0
						self.trader[i].entry_prices[position] = 0
						self.trader[i].tps[position] = 0
						self.trader[i].sls[position] = 0
						self.trader[i].current_num_of_trades += 1
						self.trader[i].stop_trading = True
						string = "Trader ID# " + str(i) + " Has Breached max Drawdown. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
						self.client_tp_sl_script.append(string)

				# If the trader is allowed to trade
				if self.trader[i].isequitybreached(self.close) == False:

					# Check if TPs or SLs are triggered
					for position in range(self.trader[i].max_trades):

						if self.close > self.trader[i].tps[position] and self.trader[i].entry_volumes[position] > 0 or self.close < self.trader[i].sls[position] and self.trader[i].entry_volumes[position] > 0:
							self.update_price(self.trader[i].entry_volumes[position] * -1)
							profit = self.trader[i].calculate_position_profit(self.close, position)
							volume = self.trader[i].entry_volumes[position]
							self.trader[i].account_balance += profit
							self.trader[i].account_balance = round(self.trader[i].account_balance, 2)
							self.trader[i].account_balance_history.append(self.trader[i].account_balance)
							self.market_maker_revenue += profit * -1
							self.market_maker_revenue = round(self.market_maker_revenue, 2)
							self.trader[i].entry_volumes[position] = 0
							self.trader[i].entry_prices[position] = 0
							self.trader[i].tps[position] = 0
							self.trader[i].sls[position] = 0
							self.trader[i].current_num_of_trades -= 1
							if self.close > self.trader[i].tps[position]:
								string = "Trader ID# " + str(i) + " Has Hit Take Profit. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
								self.client_tp_sl_script.append(string)
							else:
								string = "Trader ID# " + str(i) + " Has Been Stopped Out. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
								self.client_tp_sl_script.append(string)



						if self.close < self.trader[i].tps[position] and self.trader[i].entry_volumes[position] < 0 or self.close > self.trader[i].sls[position] and self.trader[i].entry_volumes[position] < 0:
							self.update_price(self.trader[i].entry_volumes[position]* -1)
							profit = self.trader[i].calculate_position_profit(self.close, position)
							volume = self.trader[i].entry_volumes[position]
							self.trader[i].account_balance += profit
							self.trader[i].account_balance = round(self.trader[i].account_balance, 2)
							self.trader[i].account_balance_history.append(self.trader[i].account_balance)
							self.market_maker_revenue += profit * -1
							self.market_maker_revenue = round(self.market_maker_revenue, 2)
							self.trader[i].entry_volumes[position] = 0
							self.trader[i].entry_prices[position] = 0
							self.trader[i].tps[position] = 0
							self.trader[i].sls[position] = 0
							self.trader[i].current_num_of_trades -= 1
							if self.close < self.trader[i].tps[position]:
								string = "Trader ID# " + str(i) + " Has Hit Take Profit. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
								self.client_tp_sl_script.append(string)
							else:
								string = "Trader ID# " + str(i) + " Has Been Stopped Out. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
								self.client_tp_sl_script.append(string)

					# Choose action
					action = self.trader[i].choose_action()

					if action == "buy":
						if self.trader[i].current_num_of_trades < self.trader[i].max_trades:
							position = self.trader[i].find_first_empty()
							self.trader[i].entry_prices[position] = self.ask
							self.trader[i].entry_volumes[position] = self.trader[i].volume
							self.trader[i].sls[position] = self.ask - self.trader[i].stoplength
							self.trader[i].tps[position] = self.ask + self.trader[i].stoplength * self.trader[i].riskreward
							self.update_price(self.trader[i].entry_volumes[position])
							self.trader[i].current_num_of_trades += 1
							self.trader[i].total_num_of_trades += 1
							string = "Trader ID# " + str(i) + ", TP: " + str(self.trader[i].tps[position]) + ", SL: " + str(self.trader[i].sls[position]) + " Market Long, Volume: " + str(self.trader[i].entry_volumes[position]) 
							self.client_tp_sl_script.append(string)

					if action == "sell":
						if self.trader[i].current_num_of_trades < self.trader[i].max_trades:
							position = self.trader[i].find_first_empty()
							self.trader[i].entry_prices[position] = self.bid
							self.trader[i].entry_volumes[position] = self.trader[i].volume * -1
							self.trader[i].sls[position] = self.ask + self.trader[i].stoplength
							self.trader[i].tps[position] = self.ask - self.trader[i].stoplength * self.trader[i].riskreward
							self.update_price(self.trader[i].entry_volumes[position])
							self.trader[i].current_num_of_trades += 1
							self.trader[i].total_num_of_trades += 1
							string = "Trader ID# " + str(i) + ", TP: " + str(self.trader[i].tps[position]) + ", SL: " + str(self.trader[i].sls[position]) + " Market Short, Volume: " + str(self.trader[i].entry_volumes[position])
							self.client_tp_sl_script.append(string)

					if action == "close all" and self.trader[i].current_num_of_trades > 0:
						for position in range(self.trader[i].max_trades):
							if self.trader[i].entry_prices[position] != 0:
								self.update_price(self.trader[i].entry_volumes[position]* -1)
								profit = self.trader[i].calculate_position_profit(self.close, position)
								volume = self.trader[i].entry_volumes[position]
								self.trader[i].account_balance += profit
								self.trader[i].account_balance = round(self.trader[i].account_balance, 2)
								self.trader[i].account_balance_history.append(self.trader[i].account_balance)
								self.market_maker_revenue += profit * -1
								self.market_maker_revenue = round(self.market_maker_revenue, 2)
								# Liquidate their entire inventory
								self.trader[i].entry_volumes[position] = 0
								self.trader[i].entry_prices[position] = 0
								self.trader[i].tps[position] = 0
								self.trader[i].sls[position] = 0
								self.trader[i].current_num_of_trades -= 1
								string = "Trader ID# " + str(i) + " Has Liquidated Position. Position # " + str(position) + " Closing Volume: " + str(volume * -1)
								self.client_tp_sl_script.append(string)

		self.find_most_profitable()
		ani = FuncAnimation(plt.gcf() , self.print_candles, interval = 1, repeat = False)
		plt.show()

if __name__ == "__main__":
	
	market = market()
	market.start()