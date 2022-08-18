"""
Version Differences (Altitude)
------------------------------

This example demonstrates how to calculate the
percent change along an altitude profile between MSIS version 00 and 2.
Additionally, we show the difference between densities at noon (solid)
and midnight (dashed).

"""
import matplotlib.pyplot as plt
import numpy as np

from pymsis import msis


lon = 0
lat = 70
alts = np.linspace(0, 1000, 1000)
f107 = 150
f107a = 150
ap = 7
aps = [[ap] * 7]

date = np.datetime64("2003-01-01T00:00")
output_midnight2 = msis.run(date, lon, lat, alts, f107, f107a, aps)
output_midnight0 = msis.run(date, lon, lat, alts, f107, f107a, aps, version=0)
diff_midnight = (output_midnight2 - output_midnight0) / output_midnight0 * 100

date = np.datetime64("2003-01-01T12:00")
output_noon2 = msis.run(date, lon, lat, alts, f107, f107a, aps)
output_noon0 = msis.run(date, lon, lat, alts, f107, f107a, aps, version=0)
diff_noon = (output_noon2 - output_noon0) / output_noon0 * 100


#  output is now of the shape (1, 1, 1, 1000, 11)
# Get rid of the single dimensions
diff_midnight = np.squeeze(diff_midnight)
diff_noon = np.squeeze(diff_noon)

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

_, ax = plt.subplots()
for i, label in enumerate(variables):
    if label in ("NO", "Total mass density", "Temperature"):
        # There is currently no NO data, also ignore non-number densities
        continue
    (line,) = ax.plot(diff_midnight[:, i], alts, linestyle="--")
    ax.plot(diff_noon[:, i], alts, c=line.get_color(), label=label)

ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True, ncol=4
)
ax.set_title(f"Longitude: {lon}, Latitude: {lat}")
ax.set_xlim(-50, 50)
ax.set_ylim(0, 1000)
ax.set_xlabel("Change from MSIS-00 to MSIS2 (%)")
ax.set_ylabel("Altitude (km)")

plt.show()
