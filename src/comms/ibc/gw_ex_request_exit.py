#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep, strftime
import logging
import json

from ib.ext.Contract import Contract
from optparse import OptionParser
from misc2.helpers import ContractHelper
from comms.ibgw.base_messaging import Prosumer
from comms.tws_protocol_helper import TWS_Protocol
from comms.ibc.tws_client_lib import TWS_client_manager, AbstractGatewayListener

         
class MessageListener(AbstractGatewayListener):   
    def __init__(self, name, parent):
        AbstractGatewayListener.__init__(self, name)
        self.parent = parent

    def position(self, event, message_value):  # account, contract, pos, avgCost):
        logging.info('MessageListener:%s. val->[%s]' % (event, message_value))
   
    def positionEnd(self, event, message_value):
        logging.info('MessageListener:%s. val->[%s]' % (event, message_value))
        #self.parent.stop_manager()
        
    def error(self, event, message_value):
        logging.info('MessageListener:%s. val->[%s]' % (event, message_value))  


    def gw_subscriptions(self, event, message_value):
        logging.info('MessageListener:%s. val->[%s]' % (event, message_value))
        

    def gw_subscription_changed(self, event, message_value):
        logging.info('MessageListener:%s. val->[%s]' % (event, message_value))
        

    def tickPrice(self, event, contract_key, field, price, canAutoExecute):
        logging.info('MessageListener: %s' % vars())


def test_client(kwargs):

    cm = TWS_client_manager(kwargs)
    cl = MessageListener('gw_client_message_listener', cm)
    
    cm.add_listener_topics(cl, kwargs['topics'])
    cm.start_manager()
    cm.gw_message_handler.send_message('ae_req_tds_internal', '')
    try:
        logging.info('TWS_gateway:main_loop ***** accepting console input...')
        while not cm.is_stopped(): 
        
            sleep(.45)
        
    except (KeyboardInterrupt, SystemExit):
        logging.error('TWS_client_manager: caught user interrupt. Shutting down...')
        cm.gw_message_handler.set_stop()
        
        logging.info('TWS_client_manager: Service shut down complete...')
           
    print 'end of test_client function'
      
if __name__ == '__main__':
    

    
    kwargs = {
      'name': 'simple_request',
      'bootstrap_host': 'localhost',
      'bootstrap_port': 9092,
      'redis_host': 'localhost',
      'redis_port': 6379,
      'redis_db': 0,
      'tws_host': 'localhost',
      'tws_api_port': 8496,
      'tws_app_id': 38868,
      'group_id': 'EX_REQUEST',
      'session_timeout_ms': 10000,
      'clear_offsets':  False,
      'logconfig': {'level': logging.INFO},
      'topics': ['positionEnd']
      }

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--clear_offsets", action="store_true", dest="clear_offsets",
                      help="delete all redis offsets used by this program")
    parser.add_option("-g", "--group_id",
                      action="store", dest="group_id", 
                      help="assign group_id to this running instance")
    
    (options, args) = parser.parse_args()
    for option, value in options.__dict__.iteritems():
        if value <> None:
            kwargs[option] = value
            
    #print kwargs    
      
    logconfig = kwargs['logconfig']
    logconfig['format'] = '%(asctime)s %(levelname)-8s %(message)s'    
    logging.basicConfig(**logconfig)        
    
    
    test_client(kwargs)
    
     