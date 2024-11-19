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

import pymsis


lons = range(-180, 185, 5)
lats = range(-90, 95, 5)
alt = 200
f107 = 150
f107a = 150
ap = 7
# One years worth of data at the 12th hour every day
date = np.datetime64("2003-01-01T12:00")
aps = [[ap] * 7]

output2 = pymsis.calculate(date, lons, lats, alt, f107, f107a, aps)
output0 = pymsis.calculate(date, lons, lats, alt, f107, f107a, aps, version=0)
diff = (output2 - output0) / output0 * 100
#  diff is now of the shape (1, nlons, nlats, 1, 11)
# Get rid of the single dimensions
diff = np.squeeze(diff)

fig, axarr = plt.subplots(nrows=3, ncols=3, constrained_layout=True, figsize=(8, 6))
xx, yy = np.meshgrid(lons, lats)
norm = mpl.colors.Normalize(-50, 50)
cmap = mpl.colormaps["RdBu_r"]
for i, variable in enumerate(pymsis.Variable):
    if i > 8:
        break
    ax = axarr.flatten()[i]
    mesh = ax.pcolormesh(
        xx, yy, diff[:, :, variable].T, shading="auto", norm=norm, cmap=cmap
    )
    ax.set_title(f"{variable.name}")

plt.colorbar(
    mesh, ax=axarr, label="Change from MSIS-00 to MSIS2 (%)", orientation="horizontal"
)

plt.show()
