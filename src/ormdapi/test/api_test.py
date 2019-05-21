#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import requests



def api_test(url, params, jdata=None):
    headers = ''
    r = requests.post(url, params, jdata)
    print r.content


def test_contract_info_v2():
    urls = [
    'http://localhost:5001/v2/contract?contract_info={"currency": "USD", "symbol": "BA", "sec_type":"STK"}',
    'http://localhost:5001/v2/contract?contract_info={"currency": "HKD", "symbol": "700", "sec_type":"STK"}',
    'http://localhost:5001/v2/contract?contract_info={"right": "P", "exchange": "SMART", "symbol": "GOOG", "expiry": "20190524", "currency": "USD", "sec_type": "OPT", "strike": 1160}'
    ]
    for u in urls:
        
        r = requests.get(u, {})
        print r.content


if __name__ == '__main__':

    kwargs = {
                'logconfig': {'level': logging.INFO},
                'mode': 'sync',
                
                
              }
    
    url = 'http://localhost:5001/v2/order'
    
    params = {'contract': json.dumps({"right": "", "exchange": "HKFE", "symbol": "HSI", "expiry": "20190530", "currency": "HKD", "sec_type": "FUT", "strike": 0}),
              'order_condition': json.dumps({"account": "U5550568", "order_type": "LMT", "price": 29200, "side": "BUY", "quantity": 1})}
    data = {}
    #api_test(url, params, data)
    test_contract_info_v2()
    