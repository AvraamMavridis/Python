#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 31 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

"""Server that serves clients trying to work with the database."""

import threading
import socket
import json
import random
import argparse

import sys
sys.path.append("../modules")
from Server.database import Database
from Server.Lock.readWriteLock import ReadWriteLock

# -----------------------------------------------------------------------------
# Initialize and read the command line arguments
# -----------------------------------------------------------------------------

rand = random.Random()
rand.seed()
description = """\
Server for a fortune database. It allows clients to access the database in
parallel.\
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    "-p", "--port", metavar="PORT", dest="port", type=int,
    default=rand.randint(1, 10000) + 40000, choices=range(40001, 50000),
    help="Set the port to listen to. Values in [40001, 50000]. "
         "The default value is chosen at random."
)
parser.add_argument(
    "-f", "--file", metavar="FILE", dest="file", default="dbs/fortune.db",
    help="Set the database file. Default: dbs/fortune.db."
)
opts = parser.parse_args()

db_file = opts.file
server_address = ("", opts.port)

# -----------------------------------------------------------------------------
# Auxiliary classes
# -----------------------------------------------------------------------------


class Server(object):
    """Class that provides synchronous access to the database."""

    def __init__(self, db_file):
        self.db = Database(db_file)
        self.rwlock = ReadWriteLock()

    # Public methods

    def read(self):
        #
        # Your code here.
        #
        
        self.rwlock.read_acquire()
        result = self.db.read()
        self.rwlock.read_release()
        print(" \n Read to Database called! \n")
        return result
        pass

    def write(self, fortune):
        #
        # Your code here.
        #
        print("WRITE GOT CALLED")
        self.rwlock.write_acquire()
        to_write = '\n'+fortune+'\n%'
        result = self.db.write(to_write)
        self.rwlock.write_release()
        return "wrote:" + fortune
        pass


class Request(threading.Thread):
    """ Class for handling incoming requests.
        Each request is handled in a separate thread.
    """

    def __init__(self, db_server, conn, addr):
        threading.Thread.__init__(self)
        self.db_server = db_server
        self.conn = conn
        self.addr = addr
        self.daemon = True

    # Private methods

    def process_request(self, request):
        """ Process a JSON formated request, send it to the database, and
            return the result.

            The request format is:
                {
                    "method": called_method_name,
                    "args": called_method_argumentsc
                }

            The returned result is a JSON of the following format:
                -- in case of no error:
                    {
                        "result": called_method_result
                    }
                -- in case of error:
                    {
                        "error": {
                            "name": error_class_name,
                            "args": error_arguments
                        }
                    }
        """

        try:    #print(" \n This is the request received from client" + request)
            data = json.loads(request)
            #print("this is the JSON:" + str(data))
            method = data.get('method')
            arguments = data.get('args')
            #print("Arguments to method:" + str(arguments.get("name")))
            
        #print("Method to call:" + method)
        #print("Arguments to method:" + str(arguments))
            response = {"result":database_response}
            #req = json.dumps(response)
            #return(req)
             
        except Exception as e:
            response = {"error": { "name": type(e).__name__, "args": e.args }}
        finally:
            #response = {"error": { "name": "type(e).__name__", "args": [] }}
            req = json.dumps(response)

            return(req)


        #result = getattr(data, method)()        
        #worker1 = self.conn.makefile(mode="r")
        #data = worker1.readline()
        #print("this is the server:" + data[0])
        #print(data)
        #print(data['method'])
        #print(data[0].get('method'))
        #worker = self.conn.makefile(mode="w")
        #try:
        #NEED TO SKIP IF, AND CALL DYNAMICALLY THE RECEIVED METHOD, getattr() maybe?
        #if (data.get('method') == 'read'):

                #to_call = getattr(data,"method")()   
                #print(" \n Method is Read so process the request")                 
         #       database_response = Server.read(self.db_server)
          #      response = {"result":database_response}s
           #     req = json.dumps(response)
                #print (req)
            #    return (req)
                #self.conn.sendall(req.encode('utf8'))
                #print(req) 
        #elif (data.get('method') == 'write'):
         #       print ("got into the write process")
          #      database_response = Server.write(self.db_server,data.get('args'))
           #     response = {"result":database_response}
            #    req = json.dumps(response)
                #print(req) 
                #self.conn.sendall(req.encode('utf8'))
             #   return (req)
                #print(req) 
        #except Exception as e:
         #       response = [{"error":{"name":type(e), "args":data[0].get('args')}}]
          #      req = json.dumps(response)
                #print(req) 
           #     self.conn.sendall(req.encode('utf8'))


        #if (data.get('read')):
         #   print("AGAIN CALLED")

        #
        # Your code here.
        #
        pass

    def run(self):
        try:
            # Threat the socket as a file stream.
            worker = self.conn.makefile(mode="rw")
            # Read the request in a serialized form (JSON).
            request = worker.readline()
            # Process the request.
            result = self.process_request(request)
            # Send the result.
            worker.write(result + '\n')            
            worker.flush()
        except Exception as e:
            # Catch all errors in order to prevent the object from crashing
            # due to bad connections coming from outside.
            raise 
            print("The connection to the caller has died:")
            print("\t{}: {}".format(type(e), e))
        finally:
            self.conn.close()

# -----------------------------------------------------------------------------
# The main program
# -----------------------------------------------------------------------------

print("Listening to: {}:{}".format(socket.gethostname(), opts.port))
with open("srv_address.tmp", "w") as f:
    f.write("{}:{}\n".format(socket.gethostname(), opts.port))

sync_db = Server(db_file)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(server_address)
server.listen(1)

print("Press Ctrl-C to stop the server...")

try:
    while True:
        try:
            conn, addr = server.accept()
            req = Request(sync_db, conn, addr)
            print("Serving a request from {0}".format(addr))
            req.start()
        except socket.error:
            continue
except KeyboardInterrupt:
    pass
