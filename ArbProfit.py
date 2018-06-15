Inventory_Target = 10
Inventory_TO = 900
Quote_TO = 900
exchange_list = ["GDAX","Gemini"]
mkt_list = ["GDAX_ETH/USD","Gemini_ETH/USD"]
TFbp = {"GDAX":25,"Gemini":25}
TFix = {"GDAX":0,"Gemini":0}
current_time = 34200 #9:30 am
ArbQty = None
mkt1 = None
mkt2 = None
TotalArbProfit = 0

class Msg():      
    def __init__(self,msg_type,price,volume,timestamp,mkt_name = None,):
        self.mkt_name = mkt_name
        self.msg_type = msg_type
        self.price = price
        self.volume = volume
        self.timestamp = timestamp

class inv_removed():
    def __init__(self,Qty = 0,timestamp = None):
        self.Qty = Qty
        self.timestamp = timestamp

        
a = inv_removed()
b = inv_removed()
inv_removed = {mkt_list[0]: a,mkt_list[1]:b}
ask_removed = {mkt_list[0]: a,mkt_list[1]:b}
bid_removed = {mkt_list[0]: a,mkt_list[1]:b}

class BBO():
    def __init__ (self, bid = None, ask = None):
        self.bid = bid
        self.ask = ask
        
def Get_ArbProfit(BBO):
    RawProfit = Get_RawProfit(BBO)
    TC = Get_TC(BBO)
    ArbProfit = RawProfit - TC
    return ArbProfit

def Get_RawProfit(BBO): #must call rawprofit before tc
    mkt1 = BBO.bid.mkt_name
    mkt2 = BBO.ask.mkt_name
    I1 = Inventory_Target
    if current_time - Inventory_TO < inv_removed[mkt1].timestamp:
        I1 = I1 - inv_removed[mkt1].Qty
    I2 = Inventory_Target
    if current_time - Inventory_TO < inv_removed[mkt2].timestamp:
        I2 = I2 - inv_removed[mkt2].Qty    
    ArbQty = min(min(BBO.bid.volume,I1),min(BBO.ask.volume,I2))
    RawProfit = ArbQty*BBO.bid.price - ArbQty*BBO.ask.price
    return RawProfit

def Get_TC(BBO):
    TC1 = ArbQty*BBO.bid.price*TFbp(mkt1)
    TC2 = ArbQty*BBO.ask.price*TFbp(mkt2)
    TC = TC1 + TC2
    return TC

def Get_Global_BBO():
    bid = {mkt_list[0]:None,mkt_list[1]:None}
    ask = {mkt_list[0]:None,mkt_list[1]:None}
    for i in mkt_list:
        bid[i] = Get_mkt_bid(i)
        ask[i] = Get_mkt_ask(i)
    BBO = BBO()
    if bid[mkt_list[0]>bid[mkt_list[1]:
        BBO.bid = bid[mkt_list[0]
    else
        BBO.bid = bid[mkt_list[1]
    if ask[mkt_list[1]>ask[mkt_list[0]:
        BBO.ask = ask[mkt_list[0]
    else
        BBO.ask = ask[mkt_list[1]
    return BBO
    
def Get_mkt_bid():
    return None
def Get_mkt_ask():
    return None

def Execute_Arb(ArbProfit,BBO):
    if ArbProfit > 0:
        Update_Mkt_Data(BBO)
        Total_ArbProfit = Total_ArbProfit + ArbProfit
    return None

def Update_Mkt_Data(BBO):
    return None
