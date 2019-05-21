from flask import Flask, jsonify

import json
import redis
import threading
from time import sleep
from misc2.observer import Subscriber
from flask_restful import Resource, Api, reqparse
from datetime import datetime
import traceback
from ormdapi.v1 import apiv1
from ormdapi.v2 import apiv2
from ormdapi.v2.api_utilities import ApiMessagePersistence, ApiMessageSink, TelegramApiMessageAlert
import logging



class WebConsole(Subscriber):

    TWS_LOG_REDIS_HANDLE = 'api_log'
    TWS_LOG_DEFAULT_RETRIEVE_SIZE = 100
    
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()
    
    def __init__(self, parent=None):
        Subscriber.__init__(self, 'WebConsole' )
        self.parent = parent
        self.id_message = {}
        '''
            message sink is a message queue that stores any event to be logged by the api classes
            the sink broadcasts any received message to interested subscribers: message_store and telegram bot
            message store persists events in redis 
        '''
        self.message_sink = ApiMessageSink(self.parent.get_config())
        message_store = ApiMessagePersistence(self.parent.get_redis_conn(), self.parent.get_config(), self.message_sink)
        try:
            tg_bot = TelegramApiMessageAlert(parent.kwargs['restapi.telegram_tok'], self.message_sink) 
        except KeyError:
            logging.error('Webconsole: fail to get access token for telegram bot. ') 
        self.message_sink.start()
        
        '''
            create a dedicated rs for rest api use
        '''
        kwargs = self.parent.kwargs
        self.rs = redis.Redis(kwargs['redis_host'], kwargs['redis_port'], kwargs['redis_db'])

    def get_parent(self):
        return self.parent
    
    def get_api_sink(self):
        return self.message_sink
    
    def add_resource(self):
        WebConsole.api.add_resource(apiv1.Commands, '/v1')
        WebConsole.api.add_resource(apiv1.ExitApp, '/v1/exit', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv1.Subscriptions, '/v1/subscriptions', resource_class_kwargs={'gateway_instance': self.parent})
        WebConsole.api.add_resource(apiv1.GatewaySettings, '/v1/settings', resource_class_kwargs={'gateway_instance': self.parent})
        WebConsole.api.add_resource(apiv1.AsyncOrderCRUD, '/v1/async_order/<id>', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv1.SyncOrderCRUD, '/v1/order', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv1.OrderId, '/v1/order_id', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv1.OrderStatus, '/v1/order_status/<id>', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv1.OpenOrdersStatus, '/v1/open_orders', resource_class_kwargs={'webconsole': self})
        
        
        WebConsole.api.add_resource(apiv2.SyncOrderCRUD_v2, '/v2/order', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.OrderStatus_v2, '/v2/order_status/<id>', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.OpenOrdersStatus_v2, '/v2/open_orders', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.QuoteRequest_v2, '/v2/quote', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.AcctPosition_v2, '/v2/position', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.SystemStatus_v2, '/v2/system', resource_class_kwargs={'webconsole': self})
        WebConsole.api.add_resource(apiv2.ContractInfo_v2, '/v2/contract', resource_class_kwargs={'webconsole': self})
        

    def set_stop(self):
        self.message_sink.set_stop()
        logging.info('WebConsole: setting message sink stop flag to true')
        
    def post_shutdown(self):
        self.parent.post_shutdown()
         
    '''
        implement the consumer interface
        this function gets all tws events
        forwarded internally from tws_event_handler
    '''
    def update(self, event, **param):
        if event == 'error':
            print ('webconsole override %s: %s %s %s' % (self.name, event, "<empty param>" if not param else param,
                                          
                                         '<none>' if not param else param.__class__))
            '''
                insert log into redis using lpush 
                last-in-first-out 
            '''
            param.update({'ts':datetime.today().strftime('%Y%m%d %H:%M:%S')})
            self.rs.lpush(WebConsole.TWS_LOG_REDIS_HANDLE, param)
            
    def retrieve_logs(self, num_lines=None):
        num_lines = num_lines if num_lines <> None else WebConsole.TWS_LOG_DEFAULT_RETRIEVE_SIZE
        len = min(self.rs.llen(WebConsole.TWS_LOG_REDIS_HANDLE), num_lines)
        return self.rs.lrange(WebConsole.TWS_LOG_REDIS_HANDLE, 0, len - 1)
         
        
            