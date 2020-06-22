import numpy as np
import matplotlib.pyplot as plt
import assets
import datetime
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt


tilt = 40
azimuth_pv = 0  # 0 = south facing, -90 = east facing
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
area = 12 * 1.62 * 0.98

pv1_asset = assets.pvasset(
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


area = 12 * 1.62 * 0.98
azimuth_pv = -90
pv2_asset = assets.pvasset(
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

area = 12 * 1.62 * 0.98
azimuth_pv = 0
tilt = 30
pv3_asset = assets.pvasset(
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

load = [
    1950,
    1750,
    1800,
    1650,
    1550,
    1500,
    1200,
    1200,
    1250,
    1100,
    900,
    1150,
    950,
    300,
    250,
    250,
    350,
    600,
    600,
    800,
    750,
    1000,
    1200,
    1900,
]


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

load1 = load

for n in range(364):
    load = load + load1

Load = pd.DataFrame(load, index=df.index)
Load.columns = ["Load"]


wind = df1["wind_speed"]
df = df.join(wind)
df = df.join(Load)
df2 = df.resample("1H").mean()
dataframe = df2.interpolate()
dataframe["clearness_index"] = (
    dataframe["radiation_surface"] / dataframe["radiation_toa"]
)

pv1_output = np.zeros(len(dataframe))
pv2_output = np.zeros(len(dataframe))
pv3_output = np.zeros(len(dataframe))
total = np.zeros(len(dataframe))
Net = np.zeros(len(dataframe))
Expenditure = np.zeros(len(dataframe))
Income = np.zeros(len(dataframe))

for it in range(len(dataframe)):

    time = dataframe.index[it]
    air_temp = dataframe["temperature"][it]
    G_g_horizontal = dataframe["radiation_surface"][it]
    clearness_index = dataframe["clearness_index"][it]
    wind_velocity = dataframe["wind_speed"][it]
    load = dataframe["Load"][it]

    pv1_output[it] = pv1_asset.get_output(
        time, air_temp, G_g_horizontal, clearness_index, wind_velocity
    )
    pv2_output[it] = pv2_asset.get_output(
        time, air_temp, G_g_horizontal, clearness_index, wind_velocity
    )
    pv3_output[it] = pv3_asset.get_output(
        time, air_temp, G_g_horizontal, clearness_index, wind_velocity
    )
    total[it] = pv1_output[it] + pv2_output[it] + pv3_output[it]
    Net[it] = load - total[it]


capacity = 20000
power = 10000
eff = 0.9

soc = np.zeros(len(dataframe))
output = np.zeros(len(dataframe))

for j in range(len(dataframe)):
    if j == 0:
        soc_temp = 0
    else:
        soc_temp = soc[j - 1]

    if Net[j] > 0:  # use battery
        output[j] = min(power, Net[j], eff * soc_temp)
        soc[j] = soc_temp - (1 / eff) * output[j] * 1
    elif Net[j] < 0:  # charge battery
        output[j] = max(-power, Net[j], -(1 / eff) * (capacity - soc_temp))
        soc[j] = soc_temp - eff * output[j] * 1
    elif Net[j] == 0:  # do nothing
        soc[j] = soc_temp
        output[j] = 0

net_battery = Net - output


import_battery = np.zeros(len(dataframe))
import_nobat = np.zeros(len(dataframe))
for n in range(len(dataframe)):
    if net_battery[n] > 0:
        import_battery[n] = net_battery[n]
    if Net[n] > 0:
        import_nobat[n] = Net[n]

print(import_battery.sum() * 0.13 / 1000)
print(import_nobat.sum() * 0.13 / 1000)

fig, ax = plt.subplots(2)
ax[0].plot(net_battery[0 : 24 * 4])
ax[1].plot(Net[0 : 24 * 4])
plt.show()
