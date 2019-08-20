# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 13:46:34 2017

@author: Mahfooz
"""

session_id_url_base="https://kite.zerodha.com/connect/login?api_key"
api_key="5o9woasu1obrhsj4"
secret_key="i66t1qkxs2cnpzh1ynrgm0fk9ftnnxoo"
kite_id="DM2565"
exchange="NSE"
Product="MIS"

Tax=0.00001653
Brokerage=20

# S=6,B=2,SL=1, T=11:00
Amount=20000
SellTrigger	=6
BuyTrigger	=2
SLTrigger 	=1
#MaxEnterTime=11:00:00
# 11:00 am IST is 14:30JST, 15:30IST is 19:00JST
MaxEnterTime="14:30:00"
#MarketClosingTime="15:30:00"
MarketClosingTime="18:50:00"
MaxScripsAtTime=1
# Difference in seconds b/w current time and livedata timestamp
MarketDataDelayTolerance = 180


BaseDir_W="D:\\stocks\\Kite\\AutoTradeRunner\\"
BaseDir_L=""
MarginFile="MarginMultiplier.txt"
TradingScripFile="TradingScrips.txt"
AvoidScripFile="AvoidScrips.txt"
InstrumentsFile="instruments.csv"
LiveDataFile="LiveData.csv"

MarketData_Write_Interval=20
MarketData_Read_Interval=30

OrderBookLive="OrderBookLive.csv"
OrderBookClose="OrderBookClose.csv"

holidays ="26JAN2017,24FEB2017,13MAR2017,04APR2017,14APR2017,01MAY2017,26JUN2017,15AUG2017,25AUG2017,02OCT2017,19OCT2017,20OCT2017,25DEC2017"
CloseDataLink="https://www.nseindia.com/content/historical/EQUITIES/"
#/2017/AUG/cm21AUG2017bhav.csv.zip"


