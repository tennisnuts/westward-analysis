"""
This module sets the base class for the assets in the house

Author: Oliver Nunn
"""

import numpy as np


class Non_Dispatchable:
    """ Non Dispatchable base class """
    
    def __init__(self):
        self.dispatch_type = "Non-Dispatchable"
        self.install_cost = 0
        self.lifetime = 20


class Dispatchable:
    """ Dispatchable base class """

    def __init__(self):
        self.dispatch_type = "Dispatchable"
        self.install_cost = 0
        self.lifetime = 20

class pvasset(Non_Dispatchable):
    """ 
    PV asset class 

    Input
    --------
    Capacity : PV capacity, kWh
    
