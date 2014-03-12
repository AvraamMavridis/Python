# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 31 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

"""Module for the distributed mutual exclusion implementation.

This implementation is based on the second Rikard-Agravara algorithm.
The implementation should satisfy the following requests:
    --  when starting, the peer with the smallest id in the peer list
        should get the token.
    --  access to the state of each peer (dictinaries: request, token,
        and peer_list) should be protected.
    --  the implementation should gratiously handle situations when a
        peer dies unexpectedly. All exceptions comming from calling
        peers that have died, should be handled such as the rest of the
        peers in the system are still working. Whenever a peer has been
        detected as dead, the token, request, and peer_list
        dictionaries should be updated acordingly.
    --  when the peer that has the token (either TOKEN_PRESENT or
        TOKEN_HELD) quits, it should pass the token to some other peer.
    --  For simplicity, we shall not handle the case when the peer
        holding the token dies unexpectedly.

"""

NO_TOKEN = 0
TOKEN_PRESENT = 1
TOKEN_HELD = 2


class DistributedLock(object):

    """Implementation of distributed mutual exclusion for a list of peers.

    Public methods:
        --  __init__(owner, peer_list)
        --  initialize()
        --  destroy()
        --  register_peer(pid)
        --  unregister_peer(pid)
        --  acquire()
        --  release()
        --  request_token(time, pid)
        --  obtain_token(token)
        --  display_status()

    """

    def __init__(self, owner, peer_list):
        self.peer_list = peer_list
        self.owner = owner
        self.time = 0
        self.token = None
        self.request = {}
        self.state = NO_TOKEN
        self.wait = False

    def _prepare(self, token):
        """Prepare the token to be sent as a JSON message.

        This step is necessary because in the JSON standard, the key to
        a dictionary must be a string whild in the token the key is
        integer.
        """
        return list(token.items())

    def _unprepare(self, token):
        """The reverse operation to the one above."""
        return dict(token)

    # Public methods

    def initialize(self):
        """ Initialize the state, request, and token dicts of the lock.

        Since the state of the distributed lock is linked with the
        number of peers among which the lock is distributed, we can
        utilize the lock of peer_list to protect the state of the
        distributed lock (strongly suggested).

        NOTE: peer_list must already be populated when this
        function is called.

        """
        #
        # Your code here.
        #
        #print("LIST" +str(self.peer_list))
        #self.peer_list.display_peers()
        #self.peer_list[self.owner].lock.acquire()
        
        self.peer_list.lock.acquire()
        try:
            temp = list(self.peer_list.peers.keys())
            temp.sort()
           
            print("TEMP: " +str(temp))
            for t_id in temp:
                print("TID: " +str(t_id) + " OWNER : " +str(self.owner.id)) 
                if t_id >= self.owner.id:
                    print("INITIAL IF")
                    self.state = TOKEN_PRESENT
                    self.token = {str(self.owner.id) : 0}
                break

            if ( len(temp) == 0 ):
                self.state = TOKEN_PRESENT
                      
        #print("THE STATE IS " +str(self.state))
            
            for t_id in temp :
                #elf.token = {str(self.owner.id) : 0}
                self.request[t_id] = 0
        finally:
            self.peer_list.lock.release()
        
        #print("THIS IS THE REQUEST " +str(self.request))
        
        
            
        pass

    def destroy(self):
        """ The object is being destroyed.

        If we have the token (TOKEN_PRESENT or TOKEN_HELD), we must
        give it to someone else.

        """
        #
        # Your code here.
        #
        self.peer_list.lock.acquire()
        try:
            if self.state == TOKEN_HELD:
                self.state = TOKEN_PRESENT
                temp = list(self.peer_list.peers.keys())
                temp.sort()
                for t_id in temp:
                    if self.request[t_id] > self.token[str(t_id)] and t_id!=self.owner.id:
                        self.peer_list.peers[t_id].obtain_token(self.token)
                        break
            if self.state == TOKEN_PRESENT:
                temp = list(self.peer_list.peers.keys())
                for t_id in temp:
                    if t_id != self.owner.id:
                        try:
                            self.peer_list.peers[t_id].obtain_token(self.token)
                            break
                        except Exception as e:
                            self.state = TOKEN_PRESENT
                            del self.peer_list.peers[t_id]
        finally:
            self.peer_list.lock.release()
        pass

    def register_peer(self, pid):
        """Called when a new peer joins the system."""
        
        
        
        print(" INTO REGISTER ")
        print(" THE PID IN REGISTER : " +str(pid))
        self.peer_list.lock.acquire()
        try:
            self.request[pid] = 0
            if ( self.state != NO_TOKEN ):
                self.token[str(pid)] = 0
                print("IN")
        finally:
            self.peer_list.lock.release()
        pass

    def unregister_peer(self, pid):
        """Called when a peer leaves the system."""
        
        
        
        self.peer_list.lock.acquire()
        try:
            del self.request[pid]
            if ( self.state != NO_TOKEN ):
                del self.token[str(pid)]
        finally:
            self.peer_list.lock.release()
       
        pass

    def acquire(self):
        """Called when this object tries to acquire the lock."""
        print("Trying to acquire the lock...")
        #
        # Your code here.
        #
        #wait = False
        print("TRY TO ACQUIRE")
        self.peer_list.lock.acquire()
        try:
            self.time = self.time + 1
            self.request[self.owner.id] = self.time
            #print("STATE : " +str(self.state))
            if ( self.state == NO_TOKEN ) :
                self.wait = True
                temp = list(self.peer_list.peers.keys())
                temp.sort()
                
                for t_id in temp :
                    if t_id != self.owner.id:
                        try:
                            self.peer_list.lock.release()
                            self.peer_list.peers[t_id].request_token(self.time, self.owner.id)
                           # self.wait = False
                            self.peer_list.lock.acquire()

                            
                            print("LIST IN ACQ: " +str(temp))
                        except Exception as e:
                            del self.peer_list.peers[t_id]

               
            if ( self.state == TOKEN_PRESENT ) :
                self.wait = False
                self.state = TOKEN_HELD
        finally:
            self.peer_list.lock.release()
        while self.wait:        
            pass

    def release(self):
        """Called when this object releases the lock."""
        print("Releasing the lock...")
        #
        # Your code here.
        #

        print("INTO RELEASE")
        self.peer_list.lock.acquire()
        try:
            if self.state == TOKEN_HELD :
                print("INTO FIRST IF")
                self.state = TOKEN_PRESENT
                self.time = self.time + 1
                temp = list(self.peer_list.peers.keys())
                #print("TEMP: " +str(temp)) 
                temp.sort()
              
                #position = temp.index(self.owner.id)
                for t_id in temp:
                    #print("the request is: " +(self.token))
                    print("LIST :" +str(temp))
                    if ( self.request[t_id] > self.token[str(t_id)] and t_id!=self.owner.id ):
                        print("INTO SECOND IF")
                        self.state = NO_TOKEN
                        self.token[str(self.owner.id)] = self.time
                        try:
                            self.peer_list.peers[t_id].obtain_token(self.token)
                            break         
                        except Exception as e:
                            self.state = TOKEN_PRESENT
                            #print("Exception " +type(e).__name__)
                            del self.peer_list.peerd[t_id]

        finally:            
            self.peer_list.lock.release()
        pass

    def request_token(self, time, pid):
        """Called when some other object requests the token from us."""
        #
        # Your code here.
        #
        self.peer_list.lock.acquire()
        
        try:
            self.time = self.time + 1
            self.request[pid] = max(time, self.request[pid])
            
            if (self.state == TOKEN_PRESENT and self.request[pid] > self.token[str(pid)]) :
                self.state = NO_TOKEN
                self.token[str(self.owner.id)] = self.time
               
                try:
                    self.peer_list.peers[pid].obtain_token(self.token)
                except Exception as  e:
                    self.state = TOKEN_PRESENT
                    del self.peer_list.peers[pid]
        finally:
                self.peer_list.lock.release()
            
        pass

    def obtain_token(self, token):
        """Called when some other object is giving us the token."""
        print("Receiving the token...")
        #
        # Your code here.
        #
        

        self.peer_list.lock.acquire()
        try:
            self.token = token
            print("THE OWNER: " +str(self.owner.id) + " THE REQUEST: " +str(self.request[self.owner.id]))
            if self.request[self.owner.id] > self.token[str(self.owner.id)]:
                self.state = TOKEN_HELD
                self.wait = False
            else:
                self.state = TOKEN_PRESENT
                self.wait = False
        finally:
            self.peer_list.lock.release()
        
        pass

    def display_status(self):
        """Print the status of this peer."""
        self.peer_list.lock.acquire()
        try:
            nt = self.state == NO_TOKEN
            tp = self.state == TOKEN_PRESENT
            th = self.state == TOKEN_HELD
            print("State   :: no token      : {0}".format(nt))
            print("           token present : {0}".format(tp))
            print("           token held    : {0}".format(th))
            print("Request :: {0}".format(self.request))
            print("Token   :: {0}".format(self.token))
            print("Time    :: {0}".format(self.time))
        finally:
            self.peer_list.lock.release()
