# -*- coding: utf-8 -*-
import sys, traceback
import logging
import cherrypy
import ConfigParser
import thread


class PortalServer(object):
    
    config = None
    
    
    def __init__(self, config):
        super(PortalServer, self).__init__()
        PortalServer.config = config
      

    
    
    @cherrypy.expose
    def index(self):
        
        return self.ws()
    
 
 
    
    @cherrypy.expose
    def ws(self):
        html = '%s%s/client_g.html' % (cherrypy.request.app.config['/']['tools.staticdir.root'], cherrypy.request.app.config['/static']['tools.staticdir.tmpl'])
        f = open(html)
        return f.read()
    
                 
class HTTPServe():
    
    def __init__(self, config):
        self.config = config
        
    def start_server(self):
        cherrypy.quickstart(PortalServer(self.config), '/', self.config['ws_webserver_cfg_path'])
    
    def stop_server(self):
        cherrypy.engine.exit()   
                 
if __name__ == '__main__':
            
#     logging.basicConfig(filename = "log/opt.log", filemode = 'a', 
#                         level=logging.DEBUG,
#                         format='%(asctime)s %(levelname)-8s %(message)s')      
#  
# 
#     config = ConfigParser.ConfigParser()
#     config.read("config/app.cfg")
#     host = config.get("redis", "redis.server").strip('"').strip("'")
#     port = config.get("redis", "redis.port")
#     db = config.get("redis", "redis.db")    
#     r_conn = redis.Redis(host,port,db)
#     cherrypy.quickstart(QServer(r_conn, config), '/', "config/app.cfg")
   
    if len(sys.argv) != 2:
        print("Usage: %s <config file>" % sys.argv[0])
        exit(-1)    

    cfg_path= sys.argv[1:]    
    config = ConfigParser.ConfigParser()
    if len(config.read(cfg_path)) == 0:      
        raise ValueError, "Failed to open config file" 
    
    logconfig = eval(config.get("opt_serve", "opt_serve.logconfig").strip('"').strip("'"))
    logconfig['format'] = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(**logconfig)            


    cherrypy.quickstart(PortalServer(config), '/', cfg_path[0])
    
   