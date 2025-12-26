"""
Comparison of Step vs Interpolated Geomagnetic Indices
=======================================================

This example demonstrates the difference between using step-function
(discrete 3-hourly) and linearly interpolated geomagnetic indices
when calculating atmospheric density with MSIS.

The step-function approach uses constant values within each 3-hour window,
while the interpolated approach smoothly transitions between values.
This can result in noticeable differences in computed density, especially
for high-cadence simulations.

Note: This example uses storm-time Ap mode (geomagnetic_activity=-1) which
uses the 3-hourly ap values. The default daily Ap mode (geomagnetic_activity=1)
only uses daily average Ap values where interpolation has less effect.
"""

from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

import pymsis
from pymsis.utils import get_f107_ap


# %%
# Set up the simulation
# ---------------------
# We'll compute density at a single mid-latitude location over 24 hours.

lat, lon, altitude = 45, -100, 400  # Mid-latitude, LEO altitude
start_date = datetime(2024, 5, 10, 0, 0, 0)

# 1-minute sampling for 24 hours
dates = np.array(
    [np.datetime64(start_date) + np.timedelta64(i, "m") for i in range(1440)]
)

# %%
# Calculate densities and get indices
# -----------------------------------

# Use storm-time mode (geomagnetic_activity=-1) to use 3-hourly ap values
output_step = pymsis.calculate(
    dates, lon, lat, altitude, geomagnetic_activity=-1, interpolate_indices=False
)
output_interp = pymsis.calculate(
    dates, lon, lat, altitude, geomagnetic_activity=-1, interpolate_indices=True
)

density_step = output_step[..., pymsis.Variable.MASS_DENSITY].squeeze()
density_interp = output_interp[..., pymsis.Variable.MASS_DENSITY].squeeze()

# Get the underlying indices
_, _, ap_step = get_f107_ap(dates)
_, _, ap_interp = get_f107_ap(dates, interpolate=True)

# %%
# Plot the comparison
# -------------------

fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True, layout="constrained")
plot_dates = [d.astype("datetime64[ms]").astype(datetime) for d in dates]

# Panel 1: 3-hourly ap index
ax = axes[0]
ax.plot(plot_dates, ap_step[:, 1], "b-", label="Step", linewidth=1)
ax.plot(plot_dates, ap_interp[:, 1], "r--", label="Interpolated", linewidth=1)
ax.set_ylabel("3-hour ap")
ax.set_title("Geomagnetic Index (ap)")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)

# Panel 2: Mass density
ax = axes[1]
ax.plot(plot_dates, density_step, "b-", label="Step", linewidth=1)
ax.plot(plot_dates, density_interp, "r--", label="Interpolated", linewidth=1)
ax.set_ylabel("Density (kg/m³)")
ax.set_title(f"Mass Density at {altitude} km")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)

# Panel 3: Percent difference
ax = axes[2]
pct_diff = 100 * (density_interp - density_step) / density_step
ax.plot(plot_dates, pct_diff, "g-", linewidth=1)
ax.axhline(0, color="black", linestyle="-", alpha=0.3)
ax.set_ylabel("Difference (%)")
ax.set_xlabel("Time (UTC)")
ax.set_title("Relative Difference (Interpolated - Step) / Step")
ax.grid(True, alpha=0.3)

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax.set_xlim(plot_dates[0], plot_dates[-1])

# Mark 3-hour boundaries on all panels
for ax in axes:
    for hour in range(0, 25, 3):
        boundary = start_date + timedelta(hours=hour)
        ax.axvline(boundary, color="gray", linestyle=":", alpha=0.5)

plt.show()
