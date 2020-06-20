import numpy as np
import matplotlib.pyplot as plt
import Assets
import datetime
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt


tilt = 30
azimuth_pv = 0  # 0 = south facing
latitude = 52.189
longitude = -2.028
time_zone = 0
albedo = 0.5
G_g_NOCT = 800
cell_temp_NOCT = 45
air_temp_NOCT = 20
reference_module_efficiency = 19.38 / 100
temp_coeff = 0.004
insolation_coeff = 0.12
T_coeff_P = -0.36 / 100
area = 1

pv_asset = Assets.pvasset(
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
)

df = pd.read_csv(
    "data/ninja_weather_52.1885_-2.0276_uncorrected.csv",
    skiprows=[0, 1, 2],
    index_col=[0],
    parse_dates=True,
)
df1 = pd.read_csv(
    "data/ninja_wind_52.1885_-2.0276_corrected.csv",
    skiprows=[0, 1, 2],
    index_col=[0],
    parse_dates=True,
)
wind = df1["wind_speed"]
df = df.join(wind)
df2 = df.resample("0.25H").mean()
dataframe = df2.interpolate()
dataframe["clearness_index"] = (
    dataframe["radiation_surface"] / dataframe["radiation_toa"]
)

pv1_output = np.zeros(len(dataframe))

for it in range(len(dataframe)):

    time = dataframe.index[it]
    air_temp = dataframe["temperature"][it]
    G_g_horizontal = dataframe["radiation_surface"][it]
    clearness_index = dataframe["clearness_index"][it]
    wind_velocity = dataframe["wind_speed"][it]

    pv1_output[it] = pv_asset.get_output(
        time, air_temp, G_g_horizontal, clearness_index, wind_velocity
    )


fig, ax = plt.subplots()

ax.plot(pv1_output)

plt.show()

