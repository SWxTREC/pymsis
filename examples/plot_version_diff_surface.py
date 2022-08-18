"""
Version Differences (Surface)
-----------------------------

This example demonstrates how to calculate the
percent change of all variables on a surface between
MSIS version 00 and 2.

"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from pymsis import msis


lons = range(-180, 185, 5)
lats = range(-90, 95, 5)
alt = 200
f107 = 150
f107a = 150
ap = 7
# One years worth of data at the 12th hour every day
date = np.datetime64("2003-01-01T12:00")
aps = [[ap] * 7]

output2 = msis.run(date, lons, lats, alt, f107, f107a, aps)
output0 = msis.run(date, lons, lats, alt, f107, f107a, aps, version=0)
diff = (output2 - output0) / output0 * 100
#  diff is now of the shape (1, nlons, nlats, 1, 11)
# Get rid of the single dimensions
diff = np.squeeze(diff)

variables = [
    "Total mass density",
    "N2",
    "O2",
    "O",
    "He",
    "H",
    "Ar",
    "N",
    "Anomalous O",
    "NO",
    "Temperature",
]

fig, axarr = plt.subplots(nrows=3, ncols=3, constrained_layout=True, figsize=(8, 6))
xx, yy = np.meshgrid(lons, lats)
norm = mpl.colors.Normalize(-50, 50)
cmap = mpl.cm.get_cmap("RdBu_r")
for i, ax in enumerate(axarr.flatten()):
    mesh = ax.pcolormesh(xx, yy, diff[:, :, i].T, shading="auto", norm=norm, cmap=cmap)
    ax.set_title(f"{variables[i]}")

plt.colorbar(
    mesh, ax=axarr, label="Change from MSIS-00 to MSIS2 (%)", orientation="horizontal"
)

plt.show()
