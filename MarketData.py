# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 10:25:41 2017

@author: Mahfooz
"""
#import pandas as pd
import requests
from kiteconnect import WebSocket
import time
import config
import pandas as pd

def GetSessionId():
    url = config.session_id_url_base +  config.api_key
    result = ""
    try:
        response = requests.get(url,allow_redirects=False)
        result = response.headers['Location'].split('=')[1].split('&')[0]
    except (ConnectionError, KeyError):
        print("Coould not get session ID.")
    
    return(result)    
    
    
    
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
    print("FILENAME ", filename)
    with open(filename, 'r') as file:
        print(file.readlines())
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


class MarketData( ):
    instrument_list = list()
    stock_price = dict()
    instr_to_stock = dict()
     
    
    def __init__(self,instruments,session_id):
        # Initialise.
        self.kws = WebSocket(config.api_key , session_id, config.kite_id)
            
        self.publish_file = config.BaseDir_W + "Data\\" + config.LiveDataFile
        self.instrument_list = list(instruments.values() )
        # Assign the callbacks.
        self.kws.on_tick    = self.on_tick
        self.kws.on_connect = self.on_connect
        
        self.kws.enable_reconnect(reconnect_interval=5, reconnect_tries=50)
        
        # Initialize all prices with 0. instr_to_stock = 12345:BHEL
        for key in instruments.keys():
            self.stock_price[key] = 0.0
            self.instr_to_stock[instruments[key]] = key
            
        # set time 
        self.time_counter = time.time()
        
    def start(self):
        #self.kws.connect(threaded=True)
        self.kws.connect()
        
    def on_tick(self,tick, ws):   
        tick_list = dict()
        
        # get all data in dict tick_list = 12345:145.0
        for item in tick:
            tick_list[item['instrument_token']] =  item['last_price']
        
        #print("Tick ",time.time(), tick_list)
        print("Tick ---- ",time.strftime("%H:%M:%S") )
        
        # update stock price in dict
        for key,value in tick_list.items():
            stk = self.instr_to_stock[key]  # get stock name   
            self.stock_price[stk] = value# create dict = {'BHEL': 125.65, 'WIPRO': 290.25 }
        print("stock_price dic done---- ",time.strftime("%H:%M:%S") )
        # set data in environment variable                        
        var_string = ""
        for stock,price in self.stock_price.items():
             var_string += stock + ":" + str(price) + ','   
        print("var_string formed---- ",time.strftime("%H:%M:%S") )
        # write file every x minutes
        if time.time() - self.time_counter  >= config.MarketData_Write_Interval:
            try:
                timestart = time.time()
                with open(self.publish_file, 'w') as f:
                    f.write("TimeStamp:" + time.strftime("%Y%m%d%H%M%S") + ',' +  var_string[:-1])
                    print(time.strftime("%H:%M:%S"), var_string[:-1])
                self.time_counter = time.time()
                print("TIMETAKEN: ",time.time()-timestart)
            except Exception as e:
                print("Market data write in file error. ")
                exit()
        
        
    def on_connect(self,ws):        
        ws.subscribe(self.instrument_list)
        

print("Starting...")
#Load Scrip Data. List of NSE scrips 
scrips=LoadTradingScrips()
print("Trading scrips loaded...")
#Load instruments file. Kite insrument code list to be used in getting live data. INFY:408065
instruments = LoadInstruments(scrips)
print("Instruments loaded...")
# Get the session ID (token request id)
#session_id = GetSessionId()
session_id = "dgn84rjgf6roh8jniknxjjfz52svzr2r"


# Start Getting Live market data. Start getting Live data in a thread.
LiveData = MarketData(instruments,session_id)
LiveData.start()


print("Lines after connection start")