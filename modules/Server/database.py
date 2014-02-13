# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 24 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

"""Implementation of a simple database class."""

import random



class Database(object):
    """Class containing a database implementation."""

    def __init__(self, db_file):
        self.db_file = db_file
        self.rand = random.Random()
        self.rand.seed()
        temp = open(db_file)
        self.array = temp.read().split('\n%')
        temp.close()
        pass

    def read(self):
        """Read a random location in the database."""
        randomNumber = self.rand.randrange(0,len(self.array)-1)
        return self.array[randomNumber]
        pass

    def write(self, fortune):
        """Write a new fortune to the database."""
        self.array.append(fortune)
        temp = open(self.db_file,'a')
        temp.write(fortune)
        temp.close()
        pass

