"""Generate all individual MSIS option example files.

This script creates individual plot_option_XX_*.py files for all 14 main MSIS options.
Each file is designed to work with sphinx_gallery documentation system.
"""

import os
import subprocess


# Define all options with their descriptions
OPTIONS_INFO = {
    0: {
        "name": "F10.7 Effects",
        "filename": "f107_effects",
        "description": "Solar EUV flux variations",
        "details": [
            "Solar extreme ultraviolet (EUV) radiation heating",
            "Solar flux proxy (F10.7 radio flux) dependencies",
            "Solar cycle and rotation effects on atmospheric heating",
            "Thermospheric temperature and density variations",
        ],
        "importance": [
            "Primary driver of thermospheric density variations",
            "Essential for solar cycle modeling and predictions",
            "Critical for long-term orbital decay calculations",
            "Fundamental for understanding solar-terrestrial coupling",
        ],
    },
    1: {
        "name": "Time Independent",
        "filename": "time_independent",
        "description": "Baseline atmospheric structure",
        "details": [
            "Baseline atmospheric structure that varies with latitude",
            "North-south atmospheric density and temperature gradients",
            "Geographic variations in atmospheric properties",
            "Time-independent latitude-dependent reference state",
        ],
        "importance": [
            "Provides fundamental atmospheric structure from poles to equator",
            "Essential for accurate geographic atmospheric modeling",
            "Critical for understanding latitude-dependent atmospheric behavior",
            "Foundation for all other atmospheric variations",
        ],
    },
    2: {
        "name": "Symmetric Annual",
        "filename": "symmetric_annual",
        "description": "Annual seasonal variations (symmetric)",
        "details": [
            "Seasonal atmospheric heating variations",
            "Annual solar declination effects",
            "Symmetric seasonal patterns in both hemispheres",
            "Yearly cycle in atmospheric temperature and density",
        ],
        "importance": [
            "Models primary seasonal atmospheric changes",
            "Essential for year-round atmospheric predictions",
            "Critical for understanding seasonal density variations",
            "Important for annual satellite drag variations",
        ],
    },
    3: {
        "name": "Symmetric Semiannual",
        "filename": "symmetric_semiannual",
        "description": "Semiannual atmospheric oscillations",
        "details": [
            "Twice-yearly atmospheric oscillations",
            "Semiannual density and temperature variations",
            "Atmospheric response to semiannual solar forcing",
            "Global atmospheric circulation effects",
        ],
        "importance": [
            "Captures important semiannual density variations",
            "Affects satellite drag twice per year",
            "Important for atmospheric dynamics understanding",
            "Contributes to seasonal atmospheric modeling accuracy",
        ],
    },
    4: {
        "name": "Asymmetric Annual",
        "filename": "asymmetric_annual",
        "description": "Asymmetric annual variations",
        "details": [
            "Hemisphere-dependent seasonal effects",
            "Asymmetric seasonal atmospheric responses",
            "North-south hemisphere seasonal differences",
            "Latitude-dependent annual variations",
        ],
        "importance": [
            "Models hemisphere-specific seasonal differences",
            "Important for accurate polar region modeling",
            "Captures asymmetric seasonal atmospheric responses",
            "Essential for global atmospheric accuracy",
        ],
    },
    5: {
        "name": "Asymmetric Semiannual",
        "filename": "asymmetric_semiannual",
        "description": "Asymmetric semiannual variations",
        "details": [
            "Hemisphere-specific semiannual oscillations",
            "Asymmetric twice-yearly atmospheric changes",
            "Latitude-dependent semiannual effects",
            "Complex seasonal atmospheric dynamics",
        ],
        "importance": [
            "Provides realistic hemisphere-dependent variations",
            "Important for accurate seasonal modeling",
            "Captures complex semiannual atmospheric behavior",
            "Essential for global atmospheric precision",
        ],
    },
    6: {
        "name": "Diurnal",
        "filename": "diurnal",
        "description": "Day/night atmospheric variations",
        "details": [
            "Solar heating during daytime hours",
            "Radiative cooling during nighttime",
            "Temperature-driven density changes",
            "Local time dependencies in atmospheric structure",
        ],
        "importance": [
            "Most important short-term atmospheric variation",
            "Essential for realistic atmospheric modeling",
            "Critical for satellite drag predictions",
            "Fundamental for space weather applications",
        ],
    },
    7: {
        "name": "Semidiurnal",
        "filename": "semidiurnal",
        "description": "12-hour atmospheric tidal effects",
        "details": [
            "Thermal forcing by solar heating",
            "Gravitational tidal forces (minor contribution)",
            "Atmospheric wave propagation and resonance",
            "Interaction with the Earth's rotation",
        ],
        "importance": [
            "Important for atmospheric wave dynamics",
            "Affects satellite drag calculations",
            "Key component of upper atmospheric dynamics",
            "Provides insight into atmospheric wave propagation",
        ],
    },
    8: {
        "name": "Geomagnetic Activity",
        "filename": "geomagnetic",
        "description": "Geomagnetic storm effects on atmosphere",
        "details": [
            "Joule heating from enhanced electric currents",
            "Particle precipitation heating",
            "Storm-time atmospheric expansion",
            "Enhanced atmospheric mixing and circulation",
        ],
        "importance": [
            "Critical for space weather applications",
            "Essential during geomagnetic storms",
            "Important for satellite drag during active periods",
            "Key for atmosphere-magnetosphere coupling studies",
        ],
    },
    9: {
        "name": "All UT Effects",
        "filename": "ut_effects",
        "description": "Universal Time atmospheric dependencies",
        "details": [
            "Magnetic field orientation effects",
            "UT-dependent geomagnetic coupling",
            "Diurnal variation of magnetic field geometry",
            "Solar wind-magnetosphere interaction timing",
        ],
        "importance": [
            "Important for geomagnetic coupling accuracy",
            "Essential for magnetic field orientation effects",
            "Critical for space weather applications",
            "Improves model accuracy during active conditions",
        ],
    },
    10: {
        "name": "Longitudinal",
        "filename": "longitudinal",
        "description": "Longitude-dependent atmospheric variations",
        "details": [
            "Geographic longitude effects",
            "Magnetic field declination impacts",
            "Regional atmospheric heating differences",
            "Longitude-dependent magnetic coupling",
        ],
        "importance": [
            "Captures geographic atmospheric variations",
            "Important for regional atmospheric accuracy",
            "Essential for magnetic declination effects",
            "Improves local atmospheric predictions",
        ],
    },
    11: {
        "name": "Mixed UT/Long",
        "filename": "mixed_ut_long",
        "description": "Combined UT and longitudinal effects",
        "details": [
            "Coupled universal time and longitude effects",
            "Complex temporal-spatial atmospheric variations",
            "Combined magnetic and temporal dependencies",
            "Interaction between UT and longitude effects",
        ],
        "importance": [
            "Captures complex temporal-spatial coupling",
            "Important for accurate regional predictions",
            "Essential for combined effect modeling",
            "Improves atmospheric model sophistication",
        ],
    },
    12: {
        "name": "Lower Atmosphere",
        "filename": "lower_atmosphere",
        "description": "Lower atmospheric influences",
        "details": [
            "Tropospheric and stratospheric coupling",
            "Lower atmospheric wave propagation",
            "Atmospheric tide generation from below",
            "Coupling between atmospheric regions",
        ],
        "importance": [
            "Important for atmospheric coupling studies",
            "Essential for wave propagation modeling",
            "Critical for complete atmospheric representation",
            "Improves understanding of atmospheric layers interaction",
        ],
    },
    13: {
        "name": "Lower Atm F10.7",
        "filename": "lower_atm_f107",
        "description": "Solar flux effects on lower atmosphere",
        "details": [
            "Solar flux modulation of lower atmospheric effects",
            "F10.7-dependent lower atmosphere coupling",
            "Solar cycle effects on atmospheric layers interaction",
            "Variable coupling strength with solar activity",
        ],
        "importance": [
            "Links solar activity to atmospheric coupling",
            "Important for solar cycle atmospheric studies",
            "Essential for complete solar-atmospheric modeling",
            "Improves long-term atmospheric predictions",
        ],
    },
}


def create_option_file(option_idx: int, info: dict) -> tuple[str, str]:
    """Create an individual option analysis file."""
    filename = f"plot_option_{option_idx:02d}_{info['filename']}.py"

    content = f'''"""
{option_idx:02d}. MSIS Option {option_idx}: {info["name"]}
{"=" * (len(f"{option_idx:02d}. MSIS Option {option_idx}: {info['name']}"))}

This example demonstrates the analysis of MSIS Option {option_idx},
which controls {info["description"]}. This option represents a key
physical process that affects atmospheric density variations.

Understanding how this option affects atmospheric structure is important for
atmospheric modeling, satellite operations, and space weather applications.
"""

import matplotlib.pyplot as plt

from msis_options_utils import create_option_analysis_figure

# %%
# Option {option_idx} controls {info["description"]}
# {"=" * (len(f"Option {option_idx} controls {info['description']}"))}
#
# This atmospheric effect includes:
#
{chr(10).join(f"# * {detail}" for detail in info["details"])}
#
# This analysis shows how turning OFF this option affects atmospheric density
# across different dimensions and conditions.

option_index = {option_idx}
option_name = "{info["name"]}"

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
{chr(10).join(f"# * {importance}" for importance in info["importance"])}
#
# When this option is turned OFF, these physical processes are removed
# from the atmospheric model, which can significantly impact the accuracy
# of density predictions depending on the specific application and conditions.
'''

    return filename, content


def main() -> None:
    """Generate all individual option analysis files."""
    print("Generating individual MSIS option analysis files...")

    # Determine the correct path for the output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from docs/
    output_dir = os.path.join(project_root, "examples", "individual_options")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    generated_files = []

    for option_idx, info in OPTIONS_INFO.items():
        filename, content = create_option_file(option_idx, info)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            f.write(content)

        generated_files.append(filename)
        print(f"  Created: {filename}")

    print(f"\\nGenerated {len(generated_files)} option analysis files:")
    for filename in generated_files:
        print(f"  - {filename}")

    print("\\nAll files are ready for sphinx_gallery documentation!")

    # Format all generated files with ruff
    print("\\nFormatting generated files with ruff...")
    format_files_with_ruff(output_dir, generated_files)


def format_files_with_ruff(output_dir: str, filenames: list[str]) -> None:
    """Format Python files using ruff formatter.

    Args:
        output_dir: Directory containing the files.
        filenames: List of Python file names to format.
    """
    filepaths = [os.path.join(output_dir, filename) for filename in filenames]

    try:
        # Run ruff format on all files
        cmd = ["ruff", "format", *filepaths]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603

        if result.returncode == 0:
            print(f"Successfully formatted {len(filepaths)} files with ruff")
        else:
            print(f"Warning: ruff format returned code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ruff format: {e}")
    except FileNotFoundError:
        print("Error: ruff not found. Please install ruff or run 'pip install ruff'")


if __name__ == "__main__":
    main()
