# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 31 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

import threading
import socket
import json

"""Object Request Broker

This module implements the infrastructure needed to transparently create
objects that communicate via networks. This infrastructure consists of:

--  Strub ::
        Represents the image of a remote object on the local machine.
        Used to connect to remote objects. Also called Proxy.
--  Skeleton ::
        Used to listen to incoming connections and forward them to the
        main object.
--  Peer ::
        Class that implements basic bidirectional (Stub/Skeleton)
        communication. Any object wishing to transparently interact with
        remote objects should extend this class.

"""


class ComunicationError(Exception):
    pass


class Stub(object):
    """ Stub for generic objects distributed over the network.

    This is  wrapper object for a socket.

    """

    def __init__(self, address):
        self.address = tuple(address)

    def _rmi(self, method, *args):
        #
        # Your code here.
        #
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.address)
        worker = self.s.makefile(mode='rw')
        data = {"method":method, "args":args}
        req = json.dumps(data)
        
        worker.write(req + '\n')
        worker.flush()
        answer = worker.readline()
        worker.close()
        print ("This is the answer: " +answer)
        response = json.loads(answer)
        #print ("This is the response: " +response)
        if("error" in response):
            Ex = type(response["error"]["name"],(Exception,),{})(*response["error"]["args"])
            print (answer)
            raise Ex
            print("error")
        elif("result" in response):                        
            return(response.get("result"))
      
        pass

    def __getattr__(self, attr):
        """Forward call to name over the network at the given address."""
        def rmi_call(*args):
            return self._rmi(attr, *args)
        return rmi_call


class Request(threading.Thread):
    """Run the incoming requests on the owner object of the skeleton."""

    def __init__(self, owner, conn, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        self.conn = conn
        self.owner = owner
        self.daemon = True

   
        # Your code here.
        #
    def process_request(self, request):
       
        try:   
            data = json.loads(request)
            method = data.get('method')
            arguments = data.get('args') 
            database_response = getattr(self.owner,method)(*arguments)
            response = {"result":database_response}             
        except Exception as e:
            response = {"error": { "name": type(e).__name__, "args": e.args }}
        finally:
            #response = {"error": { "name": "type(e).__name__", "args": [] }}
            req = json.dumps(response)
            return(req)      
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
            worker.close()
        except Exception as e:
            # Catch all errors in order to prevent the object from crashing
            # due to bad connections coming from outside.
            raise 
            print("The connection to the caller has died:")
            print("\t{}: {}".format(type(e), e))
        finally:
            self.conn.close()
        
        pass


class Skeleton(threading.Thread):
    """ Skeleton class for a generic owner.

    This is used to listen to an address of the network, manage incoming
    connections and forward calls to the generic owner class.

    """

    def __init__(self, owner, address):
        threading.Thread.__init__(self)
        self.address = address
        self.owner = owner
        self.daemon = True
        #
        # Your code here.
        #
       # sync_db = Server(db_file)
       
        pass

    def run(self):
        #
        # Your code here.
        #
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.address)
        server.listen(1)
        while True:
            try:
                conn, addr = server.accept()
                req = Request( self.owner, conn, addr)
                print("Serving a request from {0}".format(addr))
                req.start()
            except socket.error:
                continue
        pass


class Peer:
    """Class, extended by objects that communicate over the network."""

    def __init__(self, l_address, ns_address, ptype):
        self.type = ptype
        self.hash = ""
        self.id = -1
        self.address = self._get_external_interface(l_address)
        self.skeleton = Skeleton(self, self.address)
        self.name_service_address = self._get_external_interface(ns_address)
        self.name_service = Stub(self.name_service_address)

    # Private methods

    def _get_external_interface(self, address):
        """ Determine the external interface associated with a host name.

        This function translates the machine's host name into its the
        machine's external address, not into '127.0.0.1'.

        """

        addr_name = address[0]
        if addr_name != "":
            addrs = socket.gethostbyname_ex(addr_name)[2]
            if len(addrs) == 0:
                raise ComunicationError("Invalid address to listen to")
            elif len(addrs) == 1:
                addr_name = addrs[0]
            else:
                al = [a for a in addrs if a != "127.0.0.1"]
                addr_name = al[0]
        addr = list(address)
        addr[0] = addr_name
        return tuple(addr)

    # Public methods

    def start(self):
        """Start the communication interface."""

        self.skeleton.start()
        self.id, self.hash = self.name_service.register(self.type,
                                                        self.address)

    def destroy(self):
        """Unregister the object before removal."""

        self.name_service.unregister(self.id, self.type, self.hash)

    def check(self):
        """Checking to see if the object is still alive."""

        return (self.id, self.type)
