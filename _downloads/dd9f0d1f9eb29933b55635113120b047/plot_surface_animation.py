"""
Surface animation
-----------------

This example demonstrates how to animate the surface plot. Showing
the variations over the course of a year.

"""

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from pymsis import msis


lons = range(-180, 185, 5)
lats = range(-90, 95, 5)
alt = 200
f107 = 150
f107a = 150
ap = 4
# Diurnal data
dates = np.arange("2003-01-01", "2003-01-02", dtype="datetime64[30m]")
ndates = len(dates)
# (F107, F107a, ap) all need to be specified at the same length as dates
f107s = [f107] * ndates
f107as = [f107a] * ndates
aps = [[ap] * 7] * ndates

output = msis.run(dates, lons, lats, alt, f107s, f107as, aps)
#  output is now of the shape (ndates, nlons, nlats, 1, 11)
# Get rid of the single dimensions
output = np.squeeze(output)

i = 7  # N

fig, (ax_time, ax_mesh) = plt.subplots(
    nrows=2, gridspec_kw={"height_ratios": [1, 4]}, constrained_layout=True
)
xx, yy = np.meshgrid(lons, lats)
vmin, vmax = 1e13, 8e13
norm = matplotlib.colors.Normalize(vmin, vmax)
mesh = ax_mesh.pcolormesh(xx, yy, output[0, :, :, i].T, shading="auto", norm=norm)
plt.colorbar(
    mesh, label=f"N number density at {alt} km (/m$^3$)", orientation="horizontal"
)

time_data = output[:, len(lons) // 2, len(lats) // 2, :]
ax_time.plot(dates, time_data[:, i], c="k")
ax_time.set_xlim(dates[0], dates[-1])
ax_time.set_ylim(vmin, vmax)
ax_time.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax_time.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
time_line = ax_time.axvline(dates[0], c="r")

sun_loc = (
    180
    - (dates.astype("datetime64[s]") - dates.astype("datetime64[D]")).astype(float)
    / 86400
    * 360
)
(sun,) = ax_mesh.plot(sun_loc[0], 0, ".", c="gold", markersize=15)

date_string = dates[0].astype("O").strftime("%H:%M")
title = ax_time.set_title(f"{date_string}")
ax_mesh.set_xlabel("Longitude")
ax_mesh.set_ylabel("Latitude")


def update_surface(t):
    date_string = dates[t].astype("O").strftime("%H:%M")
    title.set_text(f"{date_string}")
    time_line.set_xdata(dates[t])
    mesh.set_array(output[t, :, :, i].T)
    sun.set_data(sun_loc[t], 0)


ani = FuncAnimation(fig, update_surface, frames=range(ndates), interval=25)

plt.show()
