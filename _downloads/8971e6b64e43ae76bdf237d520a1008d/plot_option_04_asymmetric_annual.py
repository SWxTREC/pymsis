"""
04. MSIS Option 4: Asymmetric Annual
====================================

This example demonstrates the analysis of MSIS Option 4,
which controls Asymmetric annual variations. This option represents a key
physical process that affects atmospheric density variations.

Understanding how this option affects atmospheric structure is important for
atmospheric modeling, satellite operations, and space weather applications.
"""

import matplotlib.pyplot as plt
from msis_options_utils import create_option_analysis_figure


# %%
# Option 4 controls Asymmetric annual variations
# ==============================================
#
# This atmospheric effect includes:
#
# * Hemisphere-dependent seasonal effects
# * Asymmetric seasonal atmospheric responses
# * North-south hemisphere seasonal differences
# * Latitude-dependent annual variations
#
# This analysis shows how turning OFF this option affects atmospheric density
# across different dimensions and conditions.

option_index = 4
option_name = "Asymmetric Annual"

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
# * Models hemisphere-specific seasonal differences
# * Important for accurate polar region modeling
# * Captures asymmetric seasonal atmospheric responses
# * Essential for global atmospheric accuracy
#
# When this option is turned OFF, these physical processes are removed
# from the atmospheric model, which can significantly impact the accuracy
# of density predictions depending on the specific application and conditions.
