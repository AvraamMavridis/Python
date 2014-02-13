#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 31 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

"""Client reader/writer for a fortune database."""

import sys
import socket
import json
import argparse

# -----------------------------------------------------------------------------
# Initialize and read the command line arguments
# -----------------------------------------------------------------------------


def address(path):
    addr = path.split(":")
    if len(addr) == 2 and addr[1].isdigit():
        return((addr[0], int(addr[1])))
    else:
        msg = "{} is not a correct server address.".format(path)
        raise argparse.ArgumentTypeError(msg)

description = """\
Client for a fortune database. It reads a random fortune from the database.\
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    "-w", "--write", metavar="FORTUNE", dest="fortune",
    help="Write a new fortune to the database."
)
parser.add_argument(
    "-i", "--interactive", action="store_true", dest="interactive",
    default=False, help="Interactive session with the fortune database."
)
parser.add_argument(
    "address", type=address, nargs=1, metavar="addr:port",
    help="Server address."
)
opts = parser.parse_args()
server_address = opts.address[0]

# -----------------------------------------------------------------------------
# Auxiliary classes
# -----------------------------------------------------------------------------


class ComunicationError(Exception):
    pass


class DatabaseProxy(object):
    """Class that simulates the behavior of the database class."""

    def __init__(self, server_address):
        self.address = server_address

    # Public methods

    def read(self):
        #
        # Your code here.
        #
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.address)
        worker = self.s.makefile(mode='rw')
        data = {"method":'read', "args":[]}
        req = json.dumps(data)
        #to_send = (req + "\n")       
        #self.s.send(to_send.encode('utf8'))
        #worker1 = self.s.makefile(mode="w")
        #worker1.write(req)
        #worker = self.s.makefile(mode="rw")
       
        #worker1 = self.s.makefile(mode='r')
        worker.write(req + '\n')
        worker.flush()
        answer = worker.readline()        
        response = json.loads(answer)
        #print("this is the PLAIN:" + answer + "\n")

        if("error" in response):
            Ex = type(response["error"]["name"],(Exception,),{})(*response["error"]["args"])
            print (answer)
            raise Ex
            print("error")
        elif("result" in response):
                        
            return(response.get("result"))

        #print("this is the req:" +  req)
        #request = worker1.readline()
        #print("worker request:" + request)
        #worker.write(req)
        #request = worker.readline()
        #response = json.loads(request)
        #print(response[0].get('result'))
        
        
        
        pass

    def write(self, fortune):
        #
        # Your code here.
        #

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.address)
        worker = self.s.makefile(mode='rw')
        data = {"method":'write', "args":[fortune]}
        req = json.dumps(data)
        #to_send = (req + "\n")       
        #self.s.send(to_send.encode('utf8'))
        #worker = self.s.makefile(mode="r")
        #request = worker.readline()
        #response = json.loads(request)
        worker.write(req + '\n')
        worker.flush()
        answer = worker.readline()
        response = json.loads(answer)
        self.s.close()
        return(response)
        
        pass

# -----------------------------------------------------------------------------
# The main program
# -----------------------------------------------------------------------------

# Create the database object.
db = DatabaseProxy(server_address)

if not opts.interactive:
    # Run in the normal mode.
    if opts.fortune is not None:
        db.write(opts.fortune)
    else:
        print(db.read())
        

else:
    # Run in the interactive mode.
    def menu():
        print("""\
Choose one of the following commands:
    r            ::  read a random fortune from the database,
    w <FORTUNE>  ::  write a new fortune into the database,
    h            ::  print this menu,
    q            ::  exit.\
""")

    command = ""
    menu()
    while command != "q":
        sys.stdout.write("Command> ")
        command = input()
        if command == "r":
            print(db.read())
            
        elif (len(command) > 1 and command[0] == "w" and
                command[1] in [" ", "\t"]):
            db.write(command[2:].strip())
        elif command == "h":
            menu()
