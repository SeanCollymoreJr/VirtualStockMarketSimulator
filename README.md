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
