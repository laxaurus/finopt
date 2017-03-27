import logging
from ib.ext.Contract import Contract
from misc2.helpers import ContractHelper, dict2str

class Symbol():
    key = None
    
    def __init__(self, contract):
        self.contract = contract
        self.tick_values = {}
        self.extra = {}
        self.key = ContractHelper.makeRedisKeyEx(contract)    
    
    def set_tick_value(self, id, price):
        self.tick_values[id] = price

    def get_tick_value(self, id):
        try:
            
            return self.tick_values[id]
    
        except:
            
            return None

    def get_contract(self):
        return self.contract
    
    def get_tick_values(self):
        return self.tick_values
    
    def set_extra_attributes(self, id, val):
        self.extra[id] = val
            
    def get_extra_attributes(self):
        return self.extra
    
    def get_key(self):
        return self.key
    
class Option(Symbol):
    """
        Tick Value      Description
        # 5001            impl vol
        # 5002            delta
        # 5003            gamma
        # 5004            theta
        # 5005            vega
        # 5006            premium    
    """
    
    
    IMPL_VOL = 5001
    DELTA    = 5002
    GAMMA    = 5003
    THETA    = 5004
    VEGA     = 5005
    PREMIUM  = 5006
    
    
    #[0,1,2,3,4,5,6,7,8,9,14,5001,5002,5003,5004,5005,5006]
        
    def __init__(self, contract):
        Symbol.__init__(self, contract)
        
        self.set_analytics(-1.0, -1.0, -1.0, -1.0, -1.0, -1.0)

        
    def set_analytics(self, imvol=None, delta=None, gamma=None, theta=None, vega=None, npv=None):
        
        
#         if self.analytics == None:
#             self.analytics = {}           
#         self.analytics[Option.IMPL_VOL] = imvol
#         self.analytics[Option.DELTA] = delta 
#         self.analytics[Option.GAMMA] = gamma
#         self.analytics[Option.THETA] = theta
#         self.analytics[Option.VEGA] = vega
#         self.analytics[Option.PREMIUM] = npv
        self.set_tick_value(Option.IMPL_VOL, imvol)
        self.set_tick_value[Option.DELTA] = delta 
        self.set_tick_value[Option.GAMMA] = gamma
        self.set_tick_value[Option.THETA] = theta
        self.set_tick_value[Option.VEGA] = vega
        self.set_tick_value[Option.PREMIUM] = npv        
        
        
        
    def get_analytics(self):
        raise Exception
    
        return self.analytics
    
    
    def object2kvstring(self):
        
        raise Exception
    
    
        try:           
            kv = self.object2kv()
            return '{"%s":%s, "%s":%s, "%s":%s, "%s":%s}' % ('analytics', dict2str(kv['analytics']), 
                                                    'contract', ContractHelper.contract2kvstring(self.get_contract()), 
                                                    'tick_values', dict2str(kv['tick_values']),
                                                    'extra', dict2str(kv['extra']))
        except:
            logging.error( 'Exception Option.object2kvstring')
               
        return None
    
    
    def object2kv(self):
        raise Exception
        
        try:
            analytics = self.get_analytics()
            contract =  self.get_contract()
            tick_values = self.get_tick_values()
            extra = self.get_extra_attributes()
            return {'analytics': analytics, 'contract': contract, 'tick_values': tick_values, 'extra': extra}            
        except:
            logging.error( 'Exception Option.object2kv')
               
        return None
        
