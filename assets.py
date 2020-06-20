"""
This module sets the base class for the assets in the house

Author: Oliver Nunn
"""

import numpy as np
import datetime
import math


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
    One time inputs to the system:
    ----------------------------------------------------------------------------------
    tilt : float
        tilt angle, degrees.

    azimuth_pv : float
        azimuth angle of the PV panel, degrees.

    latitude : float
        latitude of the site.

    longitude : float
        longitude of the site.

    time_zone : int
        the time zone difference from GMT i.e. Paris would be 1 (GMT + 1)

    albedo : float      default = 0.5
        albedo coefficient - depends on what surface the pv panels are on:
            hot+humid = 0.2
            dry tropical = 0.5
            snow covered = 0.9

    G_g_NOCT : float
        NOCT irradiance, W/m^2

    cell_temp_NOCT : float
        NOCT cell temperature, ºC

    air_temp_NOCT : float
        NOCT air temperature, ºC

    reference_module_efficiency : float
        reference cell efficiency, %/100

    temp_coeff : float     default = 0.004
        temperature coefficient of the pv panels, K^-1

    insolation_coeff : float     default = 0.12
        insolation coefficient of the pv panels, N/A

    T_coeff_P : float
        temperature coefficient of power for the pv panels, %/ºC

    area : float
        area of the array of pv panels, m^2
    -----------------------------------------------------------------------------------
    """

    """
    Inputs every 5s from the controller:
    -----------------------------------------------------------------------------------
    G_d_horizontal : float
        direct irradiance on a horizontal surface, kW/m^2.

    G_df_horizontal : float
        diffuse irradiance on a horizontal surface, kW/m^2

    G_g_horizontal : float
        global irradiation on a horizontal surface, kW/m^2

    air_temp : float
        ambient air temperature, ºC

    wind_velocity : float
        wind velocity on the site, m/s
    -----------------------------------------------------------------------------------
    """

    def __init__(
        self,
        tilt,
        azimuth_pv,
        latitude,
        longitude,
        time_zone,
        albedo,
        G_g_NOCT,
        cell_temp_NOCT,
        air_temp_NOCT,
        reference_module_efficiency,
        temp_coeff,
        insolation_coeff,
        T_coeff_P,
        area,
    ):
        self.tilt = tilt
        self.azimuth_pv = azimuth_pv
        self.latitude = latitude
        self.longitude = longitude
        self.time_zone = time_zone
        self.albedo = albedo
        self.G_g_NOCT = G_g_NOCT
        self.cell_temp_NOCT = cell_temp_NOCT
        self.air_temp_NOCT = air_temp_NOCT
        self.reference_module_efficiency = reference_module_efficiency
        self.temp_coeff = temp_coeff
        self.insolation_coeff = insolation_coeff
        self.T_coeff_P = T_coeff_P
        self.area = area

    """
    Irradiation model
    ---------------------------------------------------------------------------------------------------------------------------------
    """
    # correct HOMER
    def get_declination_angle(self):
        time = datetime.datetime.now()
        year = time.year
        month = time.month
        day = time.day
        day_of_year = (
            datetime.date(year, month, day) - datetime.date(year, 1, 1)
        ).days + 1
        declination_angle = 23.45 * math.sin(
            math.radians((360 / 365) * (day_of_year + 284))
        )
        return declination_angle

    # correct HOMER
    def get_hour_angle(self):
        time = datetime.datetime.now()
        year = time.year
        month = time.month
        day = time.day
        day_of_year = (
            datetime.date(year, month, day) - datetime.date(year, 1, 1)
        ).days + 1
        B = math.radians((360 / 365) * (day_of_year - 1))
        E = 3.82 * (
            0.000075
            + 0.001868 * math.cos(B)
            - 0.032077 * math.sin(B)
            - 0.014615 * math.cos(2 * B)
            - 0.04089 * math.sin(2 * B)
        )
        local_time = time.hour + time.minute / 60 + time.second / 3600
        solar_time = local_time + (self.longitude / 15) - self.time_zone + E
        hour_angle = (solar_time - 12) * 15
        return hour_angle

    # Correct HOMER
    def get_solar_zenith_angle(self):
        latitude = math.radians(self.latitude)
        declination = math.radians(self.get_declination_angle())
        hour_angle = math.radians(self.get_hour_angle())
        zenith_angle = math.acos(
            math.cos(latitude) * math.cos(declination) * math.cos(hour_angle)
            + math.sin(latitude) * math.sin(declination)
        )
        zenith_angle = math.degrees(zenith_angle)
        return zenith_angle

    # correct HOMER
    def get_incidence_angle(self):
        tilt = math.radians(self.tilt)
        pv_azimuth = math.radians(self.azimuth_pv)
        latitude = math.radians(self.latitude)
        declination = math.radians(self.get_declination_angle())
        hour_angle = math.radians(self.get_hour_angle())

        incidence = math.acos(
            math.sin(declination) * math.sin(latitude) * math.cos(tilt)
            - math.sin(declination)
            * math.cos(latitude)
            * math.sin(tilt)
            * math.cos(pv_azimuth)
            + math.cos(declination)
            * math.cos(latitude)
            * math.cos(tilt)
            * math.cos(hour_angle)
            + math.cos(declination)
            * math.sin(latitude)
            * math.sin(tilt)
            * math.cos(pv_azimuth)
            * math.cos(hour_angle)
            + math.cos(declination)
            * math.sin(tilt)
            * math.sin(pv_azimuth)
            * math.sin(hour_angle)
        )
        incidence = math.degrees(incidence)
        return incidence

    def get_G_d_t(self, G_d_horizontal):
        incidence_angle = math.radians(self.get_incidence_angle())
        zenith_angle = math.radians(self.get_solar_zenith_angle())
        G_d_t = math.cos(incidence_angle) / math.cos(zenith_angle) * G_d_horizontal
        # declination_angle = math.radians(self.get_declination_angle())
        # latitude = math.radians(self.latitude)
        # tilt = math.radians(self.tilt)
        # hour_angle = math.radians(self.get_hour_angle())
        # R_d_t = (
        #     math.sin(declination_angle) * math.sin(latitude - tilt)
        #     + math.cos(declination_angle) * math.cos(latitude - tilt)
        # ) / (
        #     math.sin(declination_angle) * math.sin(latitude)
        #     + math.cos(declination_angle) * math.cos(latitude) * math.cos(hour_angle)
        # )
        # G_d_t = R_d_t * 1  # G_d_horizontal
        # tilt = math.radians(self.tilt)
        # zenith = math.radians(self.get_solar_zenith_angle())
        # solar_azimuth = math.radians(self.get_solar_azimuth_angle())
        # pv_azimuth = math.radians(self.azimuth_pv)

        # if (tilt - zenith)<math.pi/2 && (solar_azimuth - pv_azimuth)
        # G_d_t = math.cos(tilt - zenith) * math.cos(solar_azimuth - )
        return G_d_t

    def get_G_df_t(self, G_df_horizontal):
        G_df_t = 0.5 * (1 + math.cos(math.radians(self.tilt))) * G_df_horizontal
        return G_df_t

    def get_G_aniso_df_t(self, G_d_horizontal, G_df_horizontal):
        solar_zenith_angle = self.get_solar_zenith_angle()
        incidence_angle = self.get_incidence_angle()
        time = datetime.datetime.now()
        year = time.year
        month = time.month
        day = time.day
        day_of_year = (
            datetime.date(year, month, day) - datetime.date(year, 1, 1)
        ).days + 1
        G_ext = (
            1367
            * (1 + 0.033 * math.cos(math.radians((2 * math.pi * day_of_year) / 365)))
            * math.cos(math.radians(solar_zenith_angle))
        )
        Ai = G_d_horizontal / (G_ext * math.cos(math.radians(solar_zenith_angle)))
        R_d = math.cos(math.radians(incidence_angle)) / math.cos(
            math.radians(solar_zenith_angle)
        )
        R_aniso_df_t = (
            0.5 * (1 - Ai) * (1 + math.cos(math.radians(self.tilt))) + Ai * R_d
        )
        G_aniso_df_t = R_aniso_df_t * G_df_horizontal
        return G_aniso_df_t

    # seems correct
    def get_G_r_t(self, G_g_horizontal):
        R_r = 0.5 * (1 - math.cos(math.radians(self.tilt)))
        G_r_t = R_r * self.albedo * G_g_horizontal
        return G_r_t

    def get_G_g_t(self, G_d_horizontal, G_df_horizontal, G_g_horizontal):
        G_g_t = (
            self.get_G_d_t(G_d_horizontal)
            + self.get_G_df_t(G_df_horizontal)
            + self.get_G_r_t(G_g_horizontal)
        )
        return G_g_t

    def get_G_absorbed(self, G_d_horizontal, G_df_horizontal, G_g_horizontal):
        G_absorbed = (
            self.get_G_g_t(G_d_horizontal, G_df_horizontal, G_g_horizontal)
            * 0.9  # 0.9 = absorbtion coeff approximation widely used
        )
        return G_absorbed

    """
    cell temperature model
    ---------------------------------------------------------------------------------------------------------------------------------
    """
    # correct
    def get_cell_temp(
        self, air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
    ):
        G_g_t = self.get_G_g_t(
            G_d_horizontal, G_df_horizontal, G_g_horizontal
        )  # can change if model is wrong to the absorbed version
        cell_temp = air_temp + (G_g_t / self.G_g_NOCT) * (
            9.5 / (5.7 + 3.8 * wind_velocity)
        ) * (self.cell_temp_NOCT - self.air_temp_NOCT) * (
            1 - self.reference_module_efficiency
        )
        return cell_temp

    """
    cell efficiency model
    ---------------------------------------------------------------------------------------------------------------------------------
    """
    # correct
    def get_module_eff(
        self, air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
    ):
        cell_temp = self.get_cell_temp(
            air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
        )
        G_g_t = self.get_G_absorbed(G_d_horizontal, G_df_horizontal, G_g_horizontal)
        eff = self.reference_module_efficiency * (
            1
            - self.temp_coeff * (cell_temp - 25)
            + self.insolation_coeff
            * math.log(
                G_g_t / 1000
            )  # 25 and 1000 are stc values for temp and irradiance
        )
        return eff

    """
    combined PV power model
    ---------------------------------------------------------------------------------------------------------------------------------
    """
    # correct
    def get_output(
        self, air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
    ):
        eff = self.get_module_eff(
            air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
        )
        G_absorbed = self.get_G_absorbed(
            G_d_horizontal, G_df_horizontal, G_g_horizontal
        )
        G_absorbed = 700
        T_c = self.get_cell_temp(
            air_temp, G_d_horizontal, G_df_horizontal, G_g_horizontal, wind_velocity
        )
        pv_power = (
            eff * G_absorbed * (1 - self.T_coeff_P * (T_c - 25)) * self.area
        )  # 25 is the stc temperature and is what the efficiency is based from

        # possible alterations: for eff use the reference module efficiency
        #                     : use eff but take away the temperature coeff

        return pv_power
