# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 09:54:09 2017

@author: Mahfooz
"""
import pandas as pd
import certifi
import urllib3
import requests
import shutil
import time
from kiteconnect import KiteConnect
from kiteconnect import WebSocket
import math
import datetime
import calendar
import config
from datetime import date, timedelta
import os.path
import logging
import logging.handlers
import zipfile
import sys

logging.getLogger().addHandler(logging.StreamHandler())

lg = logging.getLogger("")
lg.setLevel(logging.DEBUG)
logfile = config.BaseDir_W + "log\\" + "ATR.log"
handler = logging.handlers.RotatingFileHandler(
    logfile, maxBytes=(1048576*5), backupCount=7
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
lg.addHandler(handler)

mkt_data = dict()

# Set this token every day using below URL
# https://kite.zerodha.com/connect/login?api_key=5o9woasu1obrhsj4
#token = "obexl2myoshb6rw2l9kjbd7onqtlwizz"
token = sys.argv[1]


class MarketData( ):
    instrument_list = list()
    #stock_price = dict()
    instr_to_stock = dict()
        
    def __init__(self,instruments,public_token):
        # Initialise.
        global mkt_data
        self.kws = WebSocket(config.api_key , public_token, config.kite_id)
            
        self.publish_file = config.BaseDir_W + "Data\\" + config.LiveDataFile
        self.instrument_list = list(instruments.values() )
        # Assign the callbacks.
        self.kws.on_tick    = self.on_tick
        self.kws.on_connect = self.on_connect
        
        self.kws.enable_reconnect(reconnect_interval=5, reconnect_tries=50)
        
        # Initialize all prices with 0. instr_to_stock = 12345:BHEL
        for key in instruments.keys():
            #self.stock_price[key] = 0.0
            mkt_data[key] =  0.0
            self.instr_to_stock[instruments[key]] = key
            
        # set time 
        self.time_counter = time.time()
        
    def start(self):
        self.kws.connect(threaded=True)
        #self.kws.connect()
        
    def on_tick(self,tick, ws):  
        global mkt_data 

        for item in tick:
            #tick_list[item['instrument_token']] =  item['last_price']
            mkt_data[self.instr_to_stock[item['instrument_token']]] = item['last_price']
        
        print("Tick ------",time.strftime("%H:%M:%S"))

    def on_connect(self,ws):        
        ws.subscribe(self.instrument_list)

"""    
    def GetSessionId(self):
        url = config.session_id_url_base +  config.api_key
        result = ""
        try:
            response = requests.get(url,allow_redirects=False)
            result = response.headers['Location'].split('=')[1].split('&')[0]
        except (ConnectionError, KeyError):
            print("Coould not get session ID.")
        
        return(result)  
"""        
        
    
 

def Get_CMP(stockname):
    global mkt_data
    return(mkt_data[stockname])   
    
def Get_Request_Token():
    global token
    #token =""
    return(token)

def GetSessionId():
    url = config.session_id_url_base +'='+ config.api_key  
    print(url)
    try:
        response = requests.get(url,allow_redirects=False)
        print(response.headers)
        result = response.headers['Location'].split('=')[1].split('&')[0]
        print(result)
    except (ConnectionError, KeyError):
        print("Coould not get session ID.")
    return(result)    
    
# comapres given time string hh:mm:ss with current timeretun true if given time is less than current time
def is_time_ok(my_time_string):
    now = datetime.datetime.now()
    my_time_string = now.strftime("%Y-%m-%d") + " " + my_time_string # I am supposing the date must be the same as now    
    my_time = time.strptime(my_time_string, "%Y-%m-%d %H:%M:%S")    
    my_datetime = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=calendar.timegm(my_time))
    
    if (now <= my_datetime ):
        return True
    return False
    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

# Generic function to read delimete seperated file of two columns and return dictionary. 
def GetFileData(filename,delm=','):
    result = dict()       

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line[0] in ("\n","#"): continue
            key, val = line.split(delm)
            val = val.strip()
            if is_number(val):
                val = float(val)
            #print("Key , val :", key.strip(), val)
            result[key.strip()] = val
    return(result)

def LoadTradingScrips():
    scrips = list()
    file = config.BaseDir_W + "config\\" + config.TradingScripFile
    with open(file) as f:
        scrips = f.read().splitlines()
        
    file = config.BaseDir_W + "config\\" + config.AvoidScripFile
    with open(file) as f:
         avoid = f.read().splitlines()
    
    scrips = [x for x in scrips if x not in avoid]
    
    return(scrips)

def LoadInstruments( scrips):
    result = dict()
    file = config.BaseDir_W + "config\\" + config.InstrumentsFile
    df=pd.read_csv(file)
    
    df1 = df.loc[df['tradingsymbol'].isin(scrips)]
    df1 = df1.loc[df1['exchange'].isin(["NSE"])] 
    df1 = df1.loc[:, ['tradingsymbol','instrument_token' ]]
    #print(df1)
    for index, row in df1.iterrows():
        result[row['tradingsymbol'] ] =  row['instrument_token'] 
    
    return(result)

def GetCloseDataFileName():
    holidays = config.holidays.split(',')
    yesterday = date.today() - timedelta(1)
    while yesterday.weekday() > 4 or yesterday.strftime('%d%b%Y').upper() in holidays: # Mon-Fri are 0-4
        yesterday -= timedelta(days=1)
    return("cm" + yesterday.strftime('%d%b%Y').upper() + "bhav.csv.zip")

def DownloadCloseData(filename, fullfilename):
    url = config.CloseDataLink + filename[7:11] + '/' + filename[4:7] + '/' + filename
    try:
        r = requests.get(url, stream=True)
        with open(fullfilename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)   
    except Exception as e:
        lg.error("Could not Download 'Close Data' file : %s", url)
        exit() 

def GetCloseData():
    filedir = config.BaseDir_W + "data\\"
    zfilename = filedir + GetCloseDataFileName()    
    filename = zfilename[:-4]
    print(filedir, zfilename, filename)
    if not os.path.exists(filename):
        # Download zip file if not exist
        if not os.path.exists(zfilename):
            DownloadCloseData(GetCloseDataFileName(), zfilename )
        # unzip file
        with zipfile.ZipFile(zfilename,"r") as zip_ref:
            zip_ref.extractall(filedir)
    
    result = dict()      
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                linedata = list()
                if line[0] in ("\n","#"): continue
                linedata = line.split(',')
                if linedata[0] == "SYMBOL"   : continue
                if linedata[1] == "EQ":
                    key = linedata[0]
                    val = linedata[5]
                    val = val.strip()
                    if is_number(val):
                        val = float(val)
                    result[key.strip()] = val
    except Exception as e:
            lg.error("Could not open 'Close Data' file : %s, %s", filename, e.message)
            exit() 
    
    return(result)


class Stock:
    cmp = 0.0
    SellTrigger = 0.0
    average_price = 0.0
    AvgBuyPrice = 0.0
    BuyTriggerPrice = 0.0

    qty = 0
    
    def __init__(self,name,closedata,multiple,instruments):
        self.name = name
        self.close = closedata[name]
        self.multiple = multiple[name]
        self.SellTriggerPrice = self.GetSellTriggerPrice( ) 
        self.BuyTriggerPrice  = self.GetBuyTriggerPrice( )
        self.SLTriggerPrice   = self.GetSLTriggerPrice( )
        self.instrument = instruments[name]

    def GetSellTriggerPrice(self):
        return (self.close * (1 + config.SellTrigger / 100) ) 
    
    def GetBuyTriggerPrice(self):
        return (self.average_price * (1 - config.BuyTrigger / 100) ) 
    
    def GetSLTriggerPrice(self):
        return (self.average_price * (1 + config.SLTrigger  / 100) )
    
    def SellTriggered(self):
        if self.cmp >= self.SellTriggerPrice:
            return True
        return False
    
    def BuyTriggered(self):
        if  self.cmp <= self.BuyTriggerPrice:
            return True
        return False

    def SLTriggered(self):
        if  self.cmp >= self.SLTriggerPrice:
            return True
        return False
    
    def get_sell_qty(self):
        #return(1)
        #return(math.floor(config.Amount/self.cmp)  )   
        return(math.floor((config.Amount * self.multiple) /self.cmp)  )   
        

class MyKite:
    
    def __init__(self):
        # Get the request token
        try:
            request_token = Get_Request_Token()
            self.kite = KiteConnect(config.api_key,config.secret_key) 
            data = self.kite.request_access_token(request_token, config.secret_key )
            self.kite.set_access_token(data["access_token"])
            self.public_token = data["public_token"]
        except :
            lg.error("Error in kite connection")
            exit()

    # Place an order to kite    
    def order(self,scrip,bs,qty):
        try:     
            order_id = self.kite.order_place(tradingsymbol=scrip,  \
                                        exchange=config.exchange,   \
                                        transaction_type=bs,  \
                                        quantity=qty,          \
                                        order_type="MARKET",   \
                                        product=config.Product)
            lg.debug("Order:%s, %s, %s, %s",order_id, scrip,bs,qty)   
        except Exception as e:
            lg.error("Kite Order placement failed.")    
        return(order_id)
    #get a list of instruments from Kite
    def get_instr(self):
        try:
            return(self.kite.instruments())
        except Exception as e:
            lg.error("Kite Get instruments failed.")
            return([])

    def order_cancle(self,order_id):
        try:
            self.kite.order_cancel(order_id="order_id")
        except Exception as e:
            lg.error("Kite Order %s cancle failed.",order_id)

    def get_orders(self):
        try:
            return(self.kite.orders())
        except Exception as e:
            lg.error("Kite Get Order status failed.")

    def get_public_token(self):
        return(self.public_token)
    
class Order:
    
    def __init__(self,mykite,bs,stock,load="NO",orderid=""):
        self.bs = bs
        self.stock = stock
        self.filled_quantity = 0
        self.status = ""
        self.average_price = 0
        self.pending_quantity = 0
        self.order_timestamp = "00000000 00:00:00"
        self.price = 0
        self.cancelled_quantity = 0
        self.order_qty = 0

        # dont place new order if loading existing orders from book
        if load !=  "YES":
            if bs == "s":
                self.order_qty = self.stock.get_sell_qty()
                if self.order_qty > 0:
                    self.order_id = mykite.order(stock.name,"SELL",self.order_qty)    
            if bs == "b":
                quantity = stock.qty
                self.order_id = mykite.order(stock.name,"BUY",quantity)
        else:
            self.order_id = orderid

    def get_order_status(self,stock):
        stock.update_position()
        
    def cancle(self,mykite):
        mykite.order_cancle(self.order_id)
    

def update_orders(mykite,orders):
    orderlist = mykite.get_orders()
    for order in orderlist:
        for myorder in orders:
            if order['order_id'] == myorder.order_id:
                #if order['status'] == "COMPLETE":
                myorder.status = order['status']
                myorder.filled_quantity = order['filled_quantity']
                myorder.average_price = order['average_price']
                myorder.pending_quantity = order['pending_quantity']
                myorder.order_timestamp = order['order_timestamp']
                myorder.price = order['price']
                myorder.filled_quantity = order['filled_quantity']
                myorder.cancelled_quantity = order['cancelled_quantity']

                myorder.stock.average_price = order['average_price']
                myorder.stock.BuyTriggerPrice = myorder.stock.GetBuyTriggerPrice()
                myorder.stock.SLTriggerPrice  = myorder.stock.GetSLTriggerPrice()
                myorder.stock.qty = myorder.filled_quantity

def update_order_book(orders, type):
    
    filename = config.BaseDir_W + "data\\" + config.OrderBookClose
    if type == "Live":
        filename = filename = config.BaseDir_W + "data\\" + config.OrderBookLive

    fexists = True
    if not os.path.exists(filename):
        header = "Date,Time,OrderId,BuySell,Scrip,Close,OrderPrice,OrderQty,SLPrice,TargetPrice,Status,AvgPrice,FilledQty,CancelledQty\n"
        fexists = False
    with open(filename,'a+') as fl:
        if not fexists:
            fl.write(header)
            fexists = True
        line = ""
        for order in orders:            
            date,time = order.order_timestamp.split(' ')
            line += date + ',' + time
            line += ',' + str(order.order_id) + ',' + order.bs + ',' + order.stock.name
            line += ',' + str(order.stock.close) 
            line += ',' + str(order.price) + ',' + str(order.order_qty)
            line += ',' + str(order.stock.SLTriggerPrice) +  ',' + str(order.stock.BuyTriggerPrice )
            line += ',' + order.status + ',' + str(order.average_price) + ',' + str(order.filled_quantity) + ',' + str(order.cancelled_quantity)
            line += '\n'
            fl.write(line)

def load_orders(mykite,orders,stocks):
    # Load todays orders from file. 
    filename = filename = config.BaseDir_W + "data\\" + config.OrderBookLive
    book_orders = dict()
    if os.path.exists(filename):
        with open(filename,'r') as of:
            td = str(datetime.datetime.now().strftime("%Y-%m-%d"))
            lines = of.readlines()
            for line in lines:
                linedata = line.split(',')
                if linedata[0] != td  : continue
                book_orders[linedata[2] ]  = [linedata[2] , linedata[3], linedata[4] ]  #OrderId,BuySell,Scrip
        
        for bookorder in book_orders:
            for stock in stocks:
                if stock.name == book_orders[bookorder][2]:
                    orders.append(Order(mykite,book_orders[bookorder][1],stock,load="YES",orderid=book_orders[bookorder][0]))
        


if __name__ == "__main__":
    
    lg.info("Starting Program............")
    #Load Scrip Data. List of NSE scrips 
    scrips=LoadTradingScrips()
    lg.info("Trading scrips loaded.......")
    #load Margin multipliers. Dictionary of scrips and Multiplier (eg. TCS:30)
    file = config.BaseDir_W  + "data\\" + config.MarginFile
    multiples = GetFileData(file)
    lg.info("Margin multiplers loaded....")

    #Load instruments file. Kite insrument code list to be used in getting live data. INFY:408065
    instruments = LoadInstruments( scrips)
    lg.info("Instruments from kite loaded....")
    
    #Load last day close data. Data from NSE. TCS:2516.50
    close= GetCloseData()
    lg.info("Closing prices loaded....")
    
    # prepare list of class Stocks for tradeable scrips
    Stocks = list()
    for scrip in scrips:
        Stocks.append(Stock(scrip,close,multiples,instruments))
    lg.info("Stocks to be traded today: %s",', '.join(scrips))

    done_for_the_day = False
    
    #create Kite object. Single objects of this class should be created.
    kiteobj = MyKite()
    

    # Start Getting Live market data. Start getting Live data in a thread.
    LiveData = MarketData(instruments,kiteobj.get_public_token())
    LiveData.start()
    lg.info("Market data thread kicked off." )

    orders = list()
    # Load old order placed today
    load_orders(kiteobj,orders,Stocks)
    # get order status 
    update_orders(kiteobj,orders)

    for od in orders:
        if od.filled_quantity > 0:
            done_for_the_day = True
        #print(od.stock.name,od.order_id, od.status,od.filled_quantity,od.average_price,od.pending_quantity,od.order_timestamp,od.price,od.average_price,od.filled_quantity,od.cancelled_quantity,od.stock.average_price,od.stock.BuyTriggerPrice,od.stock.SLTriggerPrice)

    lg.info("Starting the the loop......")
    #print("Starting loop...")
    while True:
        lg.debug("%16s,%16s,%16s,%8s,%16s,%16s", "Stock","cmp","SellTriggerPrice", "Qty","BuyTriggerPrice","SLTriggerPrice")
        for stock in Stocks:
            stock.cmp = Get_CMP(stock.name)
            #lg.debug("CHECK DATA %s, cmp %s, SellTrg %s, Qty %s, BuyTrigger %s, SLTrigger %s", stock.name, stock.cmp, stock.SellTriggerPrice, stock.qty, stock.BuyTriggerPrice, stock.SLTriggerPrice)
            
            lg.debug("%16s,%16.2f,%16.2f,%8s,%16.2f,%16.2f", stock.name, stock.cmp, stock.SellTriggerPrice, stock.qty, stock.BuyTriggerPrice, stock.SLTriggerPrice)
            
            # place the short order if no current position and sell price triggered and time is less than predecided time 
            if not done_for_the_day and stock.qty == 0 and stock.SellTriggered()  and is_time_ok(config.MaxEnterTime):
                lg.debug("All SHORT conditions matched %s, %s, %s", stock.name, stock.SellTriggerPrice, stock.qty)
                orders.append(Order(kiteobj,'s',stock))
                done_for_the_day = True
            
            # Buy back when BuyTrigger hit. Book profit and exit.
            if stock.qty != 0 and stock.BuyTriggered():
                lg.debug("All EXIT conditions matched %s, %s, %s", stock.name, stock.BuyTriggerPrice, stock.qty)
                orders.append(Order(kiteobj,'b',stock))

            # Buy back if StopLoss Trigger hit. Take loss and exit.
            if stock.qty != 0 and stock.SLTriggered():
                lg.debug("All SL conditions matched %s, %s, %s", stock.name, stock.SLTriggerPrice, stock.qty)
                orders.append(Order(kiteobj,'b',stock))
           
        # get order status 
        update_orders(kiteobj,orders)
        # write order book live
        update_order_book(orders,"Live")

        # if Max enter time paased then cancle all pending orders
        if not is_time_ok(config.MaxEnterTime):
            done_for_the_day = True
            for order in orders:
                if order.status == 'PENDING' and order.pending_quantity >= 0:
                    order.cancle()
            lg.debug("Time to enter a trade is over.") 
                    
        # Exit when market gets closed.
        if not is_time_ok(config.MarketClosingTime):
            lg.info("Market will be closing now. Go home.")
            break

        time.sleep(config.MarketData_Read_Interval)


    # get order status 
    update_orders(kiteobj,orders)
    # write order book live
    update_order_book(orders,"Live")
    # write order book close
    update_order_book(orders,"Close")


    lg.info("-------------------- F I N I S H E D --------------------")
