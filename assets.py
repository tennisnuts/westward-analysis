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
    Capacity : float
        PV capacity, kWh

    Install_cost : float
        install cost per kWh, £
    """

    def __init__(self, capacity, install_cost=0):
        super().__init__()  # calls the parent class's __init__()
        self.capacity = capacity
        self.install_cost = install_cost

    def getoutput(self, dt, irradiance):  # call irradiance from the function.
        """
        Input
        ------
        dt : float
            Time interval, Hours

        irradiance : numpy array, len=25
            irradiance for the day
        """
