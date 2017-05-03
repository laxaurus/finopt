# -*- coding: utf-8 -*-
import sys, traceback
import logging
import json
import time, datetime
import copy
from optparse import OptionParser
from time import sleep
from misc2.observer import Subscriber, Publisher
from misc2.helpers import ContractHelper
from finopt.instrument import Symbol, Option
from rethink.option_chain import OptionsChain
from rethink.tick_datastore import TickDataStore
from rethink.portfolio_item import PortfolioItem, PortfolioRules, Portfolio
from comms.ibc.tws_client_lib import TWS_client_manager, AbstractGatewayListener



class PortfolioMonitor(AbstractGatewayListener):


   

    def __init__(self, kwargs):
        self.kwargs = copy.copy(kwargs)
        self.twsc = TWS_client_manager(kwargs)
        AbstractGatewayListener.__init__(self, kwargs['name'])
    
        self.tds = TickDataStore(kwargs['name'])
        self.tds.register_listener(self)
        self.twsc.add_listener_topics(self, kwargs['topics'])
        
        '''
            portfolios: {<account>: <portfolio>}
        '''
        self.portfolios = {}
        
        
    
    def start_engine(self):
        self.twsc.start_manager()
        self.twsc.reqPositions()
        self.starting_engine = True
        try:
            logging.info('PortfolioMonitor:main_loop ***** accepting console input...')
            menu = {}
            menu['1']="Request position" 
            menu['2']="Portfolio dump dtj"
            menu['3']="TDS dump"
            menu['4']="Request account updates"
            menu['5']="Table chart JSON"
            menu['9']="Exit"
            while True: 
                choices=menu.keys()
                choices.sort()
                for entry in choices: 
                    print entry, menu[entry]            

                selection = raw_input("Enter command:")
                if selection =='1':
                    self.twsc.reqPositions()
                elif selection == '2': 
                    for acct in self.portfolios.keys():
                        #print self.dump_portfolio(acct)
                        print self.portfolios[acct]['g_table']
                elif selection == '3': 
                    print self.tds.dump()
                elif selection == '4': 
                    for acct in self.portfolios.keys():
                        self.twsc.reqAccountUpdates(True, acct)
                elif selection == '5':
                    for acct in self.portfolios.keys():
                        print self.g_datatable_json(acct)
                elif selection == '9': 
                    self.twsc.gw_message_handler.set_stop()
                    break
                else: 
                    pass                
                
                sleep(0.15)
            
        except (KeyboardInterrupt, SystemExit):
            logging.error('PortfolioMonitor: caught user interrupt. Shutting down...')
            self.twsc.gw_message_handler.set_stop() 
            logging.info('PortfolioMonitor: Service shut down complete...')               
    
        
                
    def get_portfolio(self, account):
        try:
            return self.portfolios[account]
        except KeyError:
            self.portfolios[account] = Portfolio(account)
        return self.portfolios[account]
    
    def deduce_option_underlying(self, option):
        '''
            given an Option object, return the underlying Symbol object
        '''
        try:
            symbol_id = option.get_contract().m_symbol
            underlying_sectype = PortfolioRules.rule_map['symbol'][symbol_id]
            exchange = option.get_contract().m_exchange
            currency = option.get_contract().m_currency
            expiry = option.get_contract().m_expiry if PortfolioRules.rule_map['expiry'][symbol_id] ==  'same_month' else ''
            contractTuple = (symbol_id, underlying_sectype, exchange, currency, expiry, 0, '')
            logging.info('PortfolioMonitor:deduce_option_underlying. Deduced underlying==> %s' %
                          str(contractTuple))
            return Symbol(ContractHelper.makeContract(contractTuple))
        except KeyError:
            logging.error('PortfolioMonitor:deduce_option_underlying. Unable to deduce the underlying for the given option %s' %
                          ContractHelper.printContract(option.get_contract))
            return None
        
        
    def get_portfolio_option_chain(self, account, underlying):
        
        
        def create_oc_id(account, underlying_id, month):
            return '%s-%s-%s' % (account, underlying_id, month)
        
        underlying_id = underlying.get_contract().m_symbol
        month = underlying.get_contract().m_expiry
        oc_id = create_oc_id(account, underlying_id, month)
        oc = self.portfolios[account].is_oc_in_portfolio(oc_id)
        if oc == None:
            oc = OptionsChain(oc_id)
            oc.register_listener(self)
            oc.set_option_structure(underlying.get_contract(),
                                    PortfolioRules.rule_map['option_structure'][underlying_id]['spd_size'],
                                    PortfolioRules.rule_map['option_structure'][underlying_id]['multiplier'],
                                    PortfolioRules.rule_map['option_structure'][underlying_id]['rate'],
                                    PortfolioRules.rule_map['option_structure'][underlying_id]['div'],
                                    month,
                                    PortfolioRules.rule_map['option_structure'][underlying_id]['trade_vol'])
            
            self.portfolios[account].set_option_chain(oc_id, oc) 
            
            
        return oc
    

    
    def process_position(self, account, contract_key, position, average_cost, extra_info=None):
        
        # obtain a reference to the portfolio, if not exist create a new one 
        port = self.get_portfolio(account)
        port_item =  port.is_contract_in_portfolio(contract_key)
        if port_item:
            # update the values and recalculate p/l
            port_item.update_position(position, average_cost, extra_info)
            port_item.calculate_pl(contract_key)
            
            port.fire_table_rows_updated(port.ckey_to_row(contract_key))
        # new position 
        else:
            port_item = PortfolioItem(account, contract_key, position, average_cost)
            #port['port_items'][contract_key] = port_item
            port.set_portfolio_port_item(contract_key, port_item)
            instrument = port_item.get_instrument()
            self.tds.add_symbol(instrument)
            self.twsc.reqMktData(instrument.get_contract(), True)
            # option position
            if port_item.get_instrument_type() == 'OPT':
                '''
                    deduce option's underlying
                    resolve associated option chain by month, underlying
                    
                '''
                underlying = self.deduce_option_underlying(instrument)
                if underlying:
                    oc = self.get_portfolio_option_chain(account, underlying)
                    instrument.set_extra_attributes(OptionsChain.CHAIN_IDENTIFIER, oc.get_name())
                    oc.add_option(instrument)
                else:
                    logging.error('PortfolioMonitor:process_position. **** Error in adding the new position %s' % contract_key)
            # non options. stocks, futures that is...    
            else:
                logging.info('PortfolioMonitor:process_position. Adding a new non-option position into the portfolio [%s]' % port_item.dump())
                #port['port_items'][contract_key] = port_item
                #port.set_portfolio_port_item(contract_key, port_item)
                
            #self.dump_portfolio(account)    
            port.dump_portfolio()
            
            
            
            
            
    
    #         EVENT_OPTION_UPDATED = 'oc_option_updated'
    #         EVENT_UNDERLYING_ADDED = 'oc_underlying_added
    def oc_option_updated(self, event, update_mode, name, instrument):        
        logging.info('oc_option_updated. %s %s' % (event, vars()))
        self.tds.add_symbol(instrument)
        self.twsc.reqMktData(instrument.get_contract(), True)
        
    
    def oc_underlying_added(self, event, update_mode, name, instrument):
        
        logging.info('oc_underlying_added. %s %s' % (event, vars()))
        self.tds.add_symbol(instrument)
        self.twsc.reqMktData(instrument.get_contract(), True)

    
    def tds_event_symbol_added(self, event, update_mode, name, instrument):
        pass
        #logging.info('tds_event_new_symbol_added. %s' % ContractHelper.object2kvstring(symbol.get_contract()))
        
    
    def tds_event_tick_updated(self, event, contract_key, field, price, syms):
        
        for s in syms:
            
            if OptionsChain.CHAIN_IDENTIFIER in s.get_extra_attributes():
                results = {}
                chain_id = s.get_extra_attributes()[OptionsChain.CHAIN_IDENTIFIER]
                #logging.info('PortfolioMonitor:tds_event_tick_updated chain_id %s' % chain_id)
                
                for acct in self.portfolios:
                    
                    #if chain_id  in self.portfolios[acct]['opt_chains'].keys():
                    if chain_id in self.portfolios[acct].get_option_chains():
                        #logging.info('PortfolioMonitor:tds_event_tick_updated --> portfolio opt_chains: [  %s  ] ' % 
                        #             str(self.portfolios[acct]['opt_chains'].keys()))
                        if 'FUT' in contract_key or 'STK' in contract_key:
                            #results = self.portfolios[acct]['opt_chains'][chain_id].cal_greeks_in_chain(self.kwargs['evaluation_date'])
                            results = self.portfolios[acct].get_option_chain(chain_id).cal_greeks_in_chain(self.kwargs['evaluation_date'])
                        else:
                            #results[ContractHelper.makeRedisKeyEx(s.get_contract())] =  self.portfolios[acct]['opt_chains'][chain_id].cal_option_greeks(s, self.kwargs['evaluation_date'])
                            results[ContractHelper.makeRedisKeyEx(s.get_contract())] =  self.portfolios[acct].get_option_chain(chain_id).cal_option_greeks(s, self.kwargs['evaluation_date'])
                    #logging.info('PortfolioMonitor:tds_event_tick_updated. compute greek results %s' % results)
                        
                        #underlying_px = self.portfolios[acct]['opt_chains'][chain_id].get_underlying().get_tick_value(4)
                        
                    def update_portfolio_fields(key_greeks):
                        
                        self.tds.set_symbol_analytics(key_greeks[0], Option.IMPL_VOL, key_greeks[1][Option.IMPL_VOL])
                        self.tds.set_symbol_analytics(key_greeks[0], Option.DELTA, key_greeks[1][Option.DELTA])
                        self.tds.set_symbol_analytics(key_greeks[0], Option.GAMMA, key_greeks[1][Option.GAMMA])
                        self.tds.set_symbol_analytics(key_greeks[0], Option.THETA, key_greeks[1][Option.THETA])
                        self.tds.set_symbol_analytics(key_greeks[0], Option.VEGA, key_greeks[1][Option.VEGA])
                        
                        #if contract_key in self.portfolios[acct]['port_items']:
                        if self.portfolios[acct].is_contract_in_portfolio(contract_key):
                            #self.portfolios[acct]['port_items'][contract_key].calculate_pl(key_greeks[0]) #, underlying_px)
                            self.portfolios[acct].calculate_item_pl(contract_key)
                        
                            
                            self.portfolios[acct].fire_table_rows_updated(self.portfolios[acct].ckey_to_row(contract_key))
                            
                    if results:
                        #logging.info('PortfolioMonitor:tds_event_tick_updated ....before map')
                        map(update_portfolio_fields, list(results.iteritems()))
                        #logging.info('PortfolioMonitor:tds_event_tick_updated ....after map')
                           
                               
                    
            else:
                logging.info('PortfolioMonitor:tds_event_tick_updated ignoring uninterested ticks %s' % contract_key)
                continue
             
        


    def tds_event_symbol_deleted(self, event, update_mode, name, instrument):
        pass


    def tickPrice(self, event, contract_key, field, price, canAutoExecute):
        self.tds.set_symbol_tick_price(contract_key, field, price, canAutoExecute)


    def tickSize(self, event, contract_key, field, size):
        #self.tds.set_symbol_tick_size(contract_key, field, size)
        #logging.info('MessageListener:%s. %s: %d %8.2f' % (event, contract_key, field, size))
        pass
 
    def position(self, event, account, contract_key, position, average_cost, end_batch):
        if not end_batch:
            #logging.info('PortfolioMonitor:position. received position message contract=%s' % contract_key)
            self.process_position(account, contract_key, position, average_cost)
   
        else:
            # to be run once during start up
            # subscribe to automatic account updates
            if self.starting_engine:
                for acct in self.portfolios.keys():
                    self.portfolios[acct].g_datatable_json()
                    logging.info('PortfolioMonitor:position. generate gtable for ac: [%s]' % acct)
                    self.twsc.reqAccountUpdates(True, acct)
                    logging.info('PortfolioMonitor:position. subscribing to auto updates for ac: [%s]' % acct)
            self.starting_engine = False
                    
    '''
        the 4 account functions below are invoked by AbstractListener.update_portfolio_account.
        the original message from TWS is first wrapped into update_portfolio_account event in 
        class TWS_event_handler and then expanded by AbstractListener.update_portfolio_account
        (check tws_event_hander)
    '''

                
    def updateAccountValue(self, event, key, value, currency, account):  # key, value, currency, accountName):
        self.raw_dump(event, vars())
 
    def updatePortfolio(self, event, contract_key, position, market_price, market_value, average_cost, unrealized_PNL, realized_PNL, account):
        self.raw_dump(event, vars())
        self.process_position(account, contract_key, position, average_cost, 
                              {'market_price':market_price, 'market_value':market_value, 'unrealized_PNL': unrealized_PNL, 'realized_PNL': realized_PNL})
        
            
    def updateAccountTime(self, event, timestamp):
        self.raw_dump(event, vars())
        
    def accountDownloadEnd(self, event, account):  # accountName):
        self.raw_dump(event, vars())

 
    def error(self, event, message_value):
        logging.info('PortfolioMonitor:%s. val->[%s]' % (event, message_value))         
        
    def raw_dump(self, event, items):
        del(items['self'])
        logging.info('%s [[ %s ]]' % (event, items))      
        
        
if __name__ == '__main__':
    

    
    kwargs = {
      'name': 'portfolio_monitor',
      'bootstrap_host': 'localhost',
      'bootstrap_port': 9092,
      'redis_host': 'localhost',
      'redis_port': 6379,
      'redis_db': 0,
      'tws_host': 'localhost',
      'tws_api_port': 8496,
      'tws_app_id': 38868,
      'group_id': 'PM',
      'session_timeout_ms': 10000,
      'clear_offsets':  False,
      'logconfig': {'level': logging.INFO, 'filemode': 'w', 'filename': '/tmp/pm.log'},
      'topics': ['position', 'positionEnd', 'tickPrice', 'update_portfolio_account'],
      'seek_to_end': ['*'],
      'interested_position_types': {'symbol': ['HSI', 'MHI'], 'instrument_type': ['OPT', 'FUT']}

      
      }

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--clear_offsets", action="store_true", dest="clear_offsets",
                      help="delete all redis offsets used by this program")
    parser.add_option("-g", "--group_id",
                      action="store", dest="group_id", 
                      help="assign group_id to this running instance")
    parser.add_option("-e", "--evaluation_date",
                     action="store", dest="evaluation_date", 
                     help="specify evaluation date for option calculations")   
    
    (options, args) = parser.parse_args()
    if options.evaluation_date == None:
        options.evaluation_date = time.strftime('%Y%m%d') 
    
    for option, value in options.__dict__.iteritems():
        if value <> None:
            kwargs[option] = value
    
    
            
  
      
    logconfig = kwargs['logconfig']
    logconfig['format'] = '%(asctime)s %(levelname)-8s %(message)s'    
    logging.basicConfig(**logconfig)        
    
    
    server = PortfolioMonitor(kwargs)
    server.start_engine()
    
          
        