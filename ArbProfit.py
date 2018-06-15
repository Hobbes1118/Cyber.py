from collections import deque
import random

fun_price = 100
fun_spread = 2
fun_range = 20
fun_quantity = 10
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

class inv_rmClass():
    def __init__(self,Qty = 0,timestamp = None):
        self.Qty = Qty
        self.timestamp = timestamp

        
a = deque()
b = deque()
inv_removed = {mkt_list[0]: a,mkt_list[1]:b}
ask_removed = {mkt_list[0]: a,mkt_list[1]:b}
bid_removed = {mkt_list[0]: a,mkt_list[1]:b}

class BBO_class():
    def __init__ (self, bid = None, ask = None):
        self.bid = bid
        self.ask = ask

gen_BBO = BBO_class(bid = Msg("bid",fun_price,10,0),ask = Msg("ask",fun_price+fun_spread,10,0))
BBO_array = {mkt_list[0]:gen_BBO,mkt_list[1]:gen_BBO}
for i in mkt_list:
    BBO_array[i].bid.mkt_name = i
    BBO_array[i].ask.mkt_name = i
    
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
        I1 = max(0,I1 - inv_removed[mkt1].Qty)
    I2 = Inventory_Target
    if current_time - Inventory_TO < inv_removed[mkt2].timestamp:
        I2 = max(0,I2 - inv_removed[mkt2].Qty)    
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
    BBO = BBO_class()
    if bid[mkt_list[0]].price>bid[mkt_list[1]].price:
        BBO.bid = bid[mkt_list[0]]
    else:
        BBO.bid = bid[mkt_list[1]]
    if ask[mkt_list[1]].price>ask[mkt_list[0]].price:
        BBO.ask = ask[mkt_list[0]]
    else:
        BBO.ask = ask[mkt_list[1]]
    return BBO
    
def Get_mkt_bid(mkt_name):
    return BBO_array[mkt_name].bid
def Get_mkt_ask(mkt_name):
    return BBO_array[mkt_name].ask

def Execute_Arb(ArbProfit,BBO):
    if ArbProfit > 0:
        Update_Mkt_Data(BBO)
        Total_ArbProfit = Total_ArbProfit + ArbProfit
    return None

def Update_Mkt_Data(BBO):
    inv_rm = inv_rmClass(Qty = ArbQty,timestamp = current_time)
    inv_add = inv_rmClass(-ArbQty,current_time)
    inv_removed[mkt1].append(inv_add)
    inv_removed[mkt2].append(inv_rm)
    bid_removed[mkt1].append(inv_rm)
    ask_removed[mkt2].append(inv_add)
    return None

def Check_Inv_TO():
    for i in mkt_list:
        if(inv_removed[i]):
            while inv_removed[i][0].timestamp < current_time - Inventory_TO:
                inv_removed[i].popleft()
        if(bid_removed[i]):
            while bid_removed[i][0].timestamp < current_time - Inventory_TO:
                bid_removed[i].popleft()
        if(ask_removed[i]):
            while ask_removed[i][0].timestamp < current_time - Inventory_TO:
                ask_removed[i].popleft()
    return
            
def Simulate_bid_ask():
    for i in mkt_list:
        temp_price = BBO_array[i].bid.price
        probup = (temp_price - fun_price - fun_range*.5)/fun_range
        if random.random() > probup:
            BBO_array[i].bid.price += .1
            BBO_array[i].ask.price += .1
        else:
            BBO_array[i].bid.price -= .1
            BBO_array[i].ask.price -= .1
        if random.random() > .5:
            BBO_array[i].bid.volume +=1
        else:
            BBO_array[i].bid.volume -=1
        if random.random() > .5:
            BBO_array[i].ask.volume +=1
        else:
            BBO_array[i].ask.volume -=1
        BBO_array[i].ask.volume = max(1,BBO_array[i].ask.volume)
        BBO_array[i].bid.volume = max(1,BBO_array[i].bid.volume)
    return

for minute in range(0,24*60):
    current_time += 60
    Simulate_bid_ask()
    Check_Inv_TO()
    BBO = Get_Global_BBO()
    Get_ArbProfit(BBO)
    if ArbProfit > 0:
        Execute_Arb(ArbProfit,BBO)
    if(current_time%3600 == 0):
        print(ArbProfit)
        print("GDAX bid price: " + BBO_array[mkt_list[0]].bid.price)
        print("GDAX ask price: " + BBO_array[mkt_list[0]].ask.price)
        print("GDAX bid volume: " + BBO_array[mkt_list[0]].bid.volume)
        print("GDAX ask volume: " + BBO_array[mkt_list[0]].ask.volume)
        print("Gemini bid price: " + BBO_array[mkt_list[1]].bid.price)
        print("Gemini ask price: " + BBO_array[mkt_list[1]].ask.price)
        print("Gemini bid volume: " + BBO_array[mkt_list[1]].bid.volume)
        print("Gemini ask volume: " + BBO_array[mkt_list[1]].ask.volume)
