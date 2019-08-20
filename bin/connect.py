# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 21:25:13 2017

@author: Mahfooz
"""

from kiteconnect import KiteConnect
import requests


def GetSessionId():
    url = "https://kite.zerodha.com/connect/login?api_key=5o9woasu1obrhsj4" 
    print(url)
    try:
        response = requests.get(url,allow_redirects=False)
        print(response.headers)
        result = response.headers['Location'].split('=')[1].split('&')[0]
        print(result)
        
    except (ConnectionError, KeyError):
        print("Coould not get session ID.")
    return(result) 

#kite = KiteConnect(api_key="5o9woasu1obrhsj4",)
kite = KiteConnect("5o9woasu1obrhsj4","i66t1qkxs2cnpzh1ynrgm0fk9ftnnxoo")
# request token = m68tv6779w8tw010haiippmymamy5uw1

# Redirect the user to the login url obtained
# from kite.login_url(), and receive the request_token
# from the registered redirect url after the login flow.
# Once you have the request_token, obtain the access_token
# as follows.

print(kite.login_url())

sid = GetSessionId()
#data = kite.request_access_token("ylkjglomyii2grltf3lupwb06uxouihy", "i66t1qkxs2cnpzh1ynrgm0fk9ftnnxoo")
data = kite.request_access_token(sid, "i66t1qkxs2cnpzh1ynrgm0fk9ftnnxoo")
print("######################################")
kite.set_access_token(data["access_token"])

print(data["access_token"])

# Place an order
try:
	order_id = kite.order_place(tradingsymbol="WIPRO",
					exchange="NSE",
					transaction_type="BUY",
					quantity=1,
					order_type="MARKET",
					product="NRML")
    #print("Order placed. ID is", order_id)
    

	

	print("Order placed. ID is", order_id)
except Exception as e:
	print("Order placement failed", e.message)

# Fetch all orders
#kite.orders()

# Get instruments
#kite.instruments()
