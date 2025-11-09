"""
13. MSIS Option 13: Lower Atm F10.7
===================================

This example demonstrates the analysis of MSIS Option 13,
which controls Solar flux effects on lower atmosphere. This option represents a key
physical process that affects atmospheric density variations.

Understanding how this option affects atmospheric structure is important for
atmospheric modeling, satellite operations, and space weather applications.
"""

import matplotlib.pyplot as plt
from msis_options_utils import create_option_analysis_figure


# %%
# Option 13 controls Solar flux effects on lower atmosphere
# =========================================================
#
# This atmospheric effect includes:
#
# * Solar flux modulation of lower atmospheric effects
# * F10.7-dependent lower atmosphere coupling
# * Solar cycle effects on atmospheric layers interaction
# * Variable coupling strength with solar activity
#
# This analysis shows how turning OFF this option affects atmospheric density
# across different dimensions and conditions.

option_index = 13
option_name = "Lower Atm F10.7"

fig = create_option_analysis_figure(option_index, option_name)

# %%
# Understanding the Results
# =========================
#
# **Panel A (Altitude Profiles)**: Shows how this effect varies with altitude
# and between different seasonal and diurnal conditions. Look for differences
# between the four curves to understand temporal variability.
#
# **Panel B (Geographic Map)**: Reveals the global pattern of this atmospheric
# effect. The contour plot shows percentage changes when the option is turned OFF
# compared to the baseline (all options ON).
#
# **Panel C (Diurnal Cycle)**: Demonstrates how this effect varies throughout
# a 24-hour period at a fixed location (45°N, 0°E, 300 km altitude).
#
# **Panel D (Seasonal Cycle)**: Shows how the strength of this effect
# varies throughout the year, revealing seasonal dependencies.

plt.show()

# %%
# Physical Importance
# ===================
#
# This atmospheric effect is important because:
#
# * Links solar activity to atmospheric coupling
# * Important for solar cycle atmospheric studies
# * Essential for complete solar-atmospheric modeling
# * Improves long-term atmospheric predictions
#
# When this option is turned OFF, these physical processes are removed
# from the atmospheric model, which can significantly impact the accuracy
# of density predictions depending on the specific application and conditions.
