Required 3rd party Libraries:

1. numpy
2. mpl_finance
3. matplotlib
4. pandas

![VirtualStockMarketSimulator](https://github.com/SeanCollymoreJr/VirtualStockMarketSimulator/assets/174896134/cfb9c089-1ab0-4643-a684-855865e1a54a)

What's Happening Under The Hood:

An environment is setup that simulates realistic tick changes when buying or selling occurs. The enviornment is initialized with 1,000 agents (In this case)
and at each new timestep a new agent is selected as we iterate through each agent. At this point the agent has the ability to buy, sell, close position, or do nothing.
If the agent buys, sells, or closes their positions a tick is counted and price is updated. IMPORTANT: Every time price changes we have to check whether any active
stop losses or take profits have been crossed. This means that we have to loop through every active position in the environment. In this case a linked list is used to
keep track of active positions and which agent the position belongs to. This implementation of a linked list allowed for immense optimizational speed ups!

The algorithm can be run in "live-mode" or "simulate mode". In "live mode" the candles are updated tick by tick and the console prints each timestep action.
In "simulate mode" the algorithm runs through until completion until the entire chart is complete, without animating the chart or printing to the console.

<img width="800px" height="auto" src="https://github.com/SeanCollymoreJr/VirtualStockMarketSimulator/assets/174896134/bf879752-40f5-487d-ae10-53a7dc747dfa" style="padding-right:10px;" />

if you look at the highlighted section in green you can see that many agents are getting stopped out of their positions. This represents "liquidity" as a large amount
of orders (positions) are being closed. This event forces the stock price in a one particular direction; As you can see in the image above the stock price is rising sharply.

<img width="800px" height="auto" src="https://github.com/SeanCollymoreJr/VirtualStockMarketSimulator/assets/174896134/93015661-d457-43b3-8b93-a9db3e5f7779" style="padding-right:10px;" />

As time progressed the market continued to fall further and further.
