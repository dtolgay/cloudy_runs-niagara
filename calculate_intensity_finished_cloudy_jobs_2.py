########################### Import modules
import numpy as np
import pandas as pd

# import matplotlib
# import matplotlib.pyplot as plt
# plt.style.use("seaborn-poster")

from scipy import integrate
from time import time


# # Some functions need to be defined here
# def meters_to_Ghz_calculator(wavelength_in_meters):
#     c = 299792458  # m/s
#     frequency_in_Ghz = c / wavelength_in_meters * 1e-9
#     return frequency_in_Ghz


# def return_ergs_per_second2radio_units(rest_frequency):
#     ergs_per_second2solar_luminosity = (3.826e33) ** (-1)
#     solar_luminosity2radio_units = (3e-11 * (rest_frequency**3)) ** (-1)  # Rest frequency should be in Ghz
#     ergs_per_second2radio_units = (ergs_per_second2solar_luminosity * solar_luminosity2radio_units)

#     return ergs_per_second2radio_units


########################### Global variables
# TRAIN_DATA_FILE_PATH = "/scratch/m/murray/dtolgay/cloudy_runs/z_0/cr_1_CO87_CII_H_O3/cr_1_CO87_CII_H_O3_metallicity_minus2_minus3point5"
TRAIN_DATA_FILE_PATH = "/home/m/murray/dtolgay/scratch/cloudy_runs/z_3/m12f_res7100_md_test"



# GLOBAL VARIABLES
# There is an important consideration here. The keys in the EMISSION_WAVELENGHTS and COLUMNS_EMISSIVITY for the lines that I want to convert units 
# must match!!!

# EMISSION_WAVELENGHTS = {
#     "CO10": 2600.05e-6,  # meter
#     "CO21": 1300.05e-6,
#     "CO32": 866.727e-6,
#     "CO43": 650.074e-6,
#     "CO54": 520.08e-6,
#     "CO65": 433.438e-6,
#     "CO76": 371.549e-6,
#     "CO87": 325.137e-6,
#     "13CO": 2719.67e-6,
# }

COLUMNS_EMISSIVITY = [
    "radius",
    "ly_alpha",
    "h_alpha",
    "h_beta",
    "CO10",
    "CO21",
    "CO32",
    "CO43",
    "CO54",
    "CO65",
    "CO76",
    "CO87",
    "13CO",
    "C2",
    "O3_88um",
    "O3_5006um",
    "O3_4958um",
]

########################### Functions
def find_converged_run(cloudy_em_str: np.ndarray, threshold: float = 0) -> np.ndarray:
    """
    To use the coverged value, I will look at the radius values in the file. If radius decreases to initial radius and simulations
    ran one more time starting from the beginning then it means that in the first run it is not coverged and simulation was run again
    Second run gives the converged value. Use the second run.
    """

    index = 0
    for i in range(len(cloudy_em_str) - 1):
        if (cloudy_em_str[i][0] - cloudy_em_str[i + 1][0]) > threshold:
            index = i + 1

    cloudy_em_str = cloudy_em_str[index:]

    return cloudy_em_str


def get_L_line(center):

    '''
    This code is dependent on the global array: COLUMNS_EMISSIVITY. 
    First .out file is read. If the runs ran properly, indicated by OK at the end of the file
    line luminosity calculation starts. If not functions returns NaN and center values. 
    If the run is OK, then converged data is found by using the find_converged_run function and that data is used. Cloudy outputs distance from the face of
    the cloud, but to integrate for gas particles, I have to express the integration parameter (distance) starting from the center of the cloud so I subtract
    max distance and reverse the array. The resulting value 'r' is my integration parameter. Then I am reversing all the other columns of the data and matching
    them with the names of the lines by using the COLUMNS_EMISSIVITY. COLUMNS_EMISSIVITY stores all of the names of the lines that I am expecting to have in 
    the *_em.str file. Then I am reversing the data in each column. Finally I am taking the path integral of all of the lines (all columns except radius).
    To process the returned data properly I am converting dictionary to numpy array.
    '''

    # fdir = f"hden{center[1]:.3f}_metallicity{center[0]:.3f}_turbulence{center[2]:.3f}_isrf{center[3]:.3f}_radius{center[4]:.3f}"
    fdir = f"hden{center['log_hden']:.5f}_metallicity{center['log_metallicity']:.5f}_turbulence{center['log_turbulence']:.5f}_isrf{center['log_isrf']:.5f}_radius{center['log_radius']:.5f}"

    try:
        with open(f"{TRAIN_DATA_FILE_PATH}/{fdir}/{fdir}.out", "r") as file:
            lines = file.readlines()
            last_line = lines[-1]

        if "OK" == last_line[len(last_line) - 4 : len(last_line) - 2]:
            cloudy_em_str = np.loadtxt(
                fname=f"{TRAIN_DATA_FILE_PATH}/{fdir}/{fdir}_em.str"
            )
            # Only use the coverged run
            cloudy_em_str = find_converged_run(cloudy_em_str=cloudy_em_str)

            # Create a dictionary to store separate arrays for each column
            emissivity_arrays = {
                column_name: cloudy_em_str[:, idx] for idx, column_name in enumerate(COLUMNS_EMISSIVITY)
            }

            path_integrals = {}
            for key in emissivity_arrays:
                if key != "radius":
                    path_integrals[key] = (
                        integrate.simpson(y=emissivity_arrays[key], x=emissivity_arrays['radius'])
                    ) # erg s^-1 cm^-2

            # Convert volume integrals into numpy array 
            path_integrals = np.array(list(path_integrals.values())) # Only get the numerical values. Don't bother returning keys.

            return path_integrals, center

        else:
            return None, center

    except Exception as e:
        print("\n")
        print(f"An error occurred: {e}")
        print(f"File {TRAIN_DATA_FILE_PATH}/{fdir}/{fdir}.out cannot read!")
        return None, center


########################### Main

# Get the file path
centers_file_path = f"{TRAIN_DATA_FILE_PATH}/centers.txt"
centers_train = np.loadtxt(fname=centers_file_path) 

print(f"Using {centers_file_path} as a center.txt file")

centers_train_df = pd.DataFrame(
    centers_train,
    columns=[
        "log_metallicity",
        "log_hden",
        "log_turbulence",
        "log_isrf",
        "log_radius",
    ],
)


start = time()

centers_and_line_luminosities = []
ok_runs = []
broken_runs = []

start_2 = time()

for row, center in centers_train_df.iterrows():
    # Get the line luminosities and file name
    result = get_L_line(center)

    if result[0] is not None:
        # Save both the line luminosites and file name of the successful runs
        centers_and_line_luminosities.append(np.append(result[1], result[0])) 
        ok_runs.append(result[1])

    else:
        centers_and_line_luminosities.append(
            np.append( result[1], [np.nan for i in range(len(COLUMNS_EMISSIVITY) - 1)] )
            ) # Return the NaN array
        broken_runs.append(result[1])

    if row % 1e4 == 1:
        print(f"{row} finished. Left {len(centers_train_df) - row}")
        stop_2 = time()
        time_passed_in_minutes = (stop_2 - start_2) / 60
        print(f"Time passed is {round(time_passed_in_minutes, 3)} minutes")


# Convert centers_and_line_luminosities to a numpy array
centers_and_line_luminosities = np.array(centers_and_line_luminosities)

end = time()
print(f"It took {round((end - start)/60, 2)} minutes to calculate line luminosities!")

print(
    f"len(ok_runs) = {len(ok_runs)} --------------------------- len(broken_runs) = {len(broken_runs)}"
)


# Create dataframe to store the successful runs.
columns = list(centers_train_df.keys())
# Get the name of the lines
columns_luminosities = [column for column in COLUMNS_EMISSIVITY if column != "radius"]
columns.extend(columns_luminosities)
successful_runs = pd.DataFrame(centers_and_line_luminosities, columns=columns)

## Writing to a file
header = """
Column 0: log_metallicity [log(Zsolar)]
Column 1: log_hden [log(cm^-3)]
Column 2: log_turbulence [log(km s^-1)]
Column 3: log_isrf [log(G0)]
Column 4: log_radius [log(pc)]
Column 5: I_ly_alpha [erg s^-1 cm^-2]
Column 6: I_h_alpha [erg s^-1 cm^-2]
Column 7: I_h_beta [erg s^-1 cm^-2]
Column 8: I_co_10 [erg s^-1 cm^-2]
Column 9: I_co_21 [erg s^-1 cm^-2]
Column 10: I_co_32 [erg s^-1 cm^-2]
Column 11: I_co_43 [erg s^-1 cm^-2]
Column 12: I_co_54 [erg s^-1 cm^-2]
Column 13: I_co_65 [erg s^-1 cm^-2]
Column 14: I_co_76 [erg s^-1 cm^-2]
Column 15: I_co_87 [erg s^-1 cm^-2]
Column 16: I_13co [erg s^-1 cm^-2]
Column 17: I_c2 [erg s^-1 cm^-2]
Column 18: I_o3_88 [erg s^-1 cm^-2]
Column 19: I_o3_5006 [erg s^-1 cm^-2]
Column 20: I_o3_4958 [erg s^-1 cm^-2]
"""

out_file_name = "I_line_values_without_reversing.txt"

np.savetxt(
    fname=f"{TRAIN_DATA_FILE_PATH}/{out_file_name}",
    X=successful_runs,
    fmt="%.8e",
    header=header,
)

print(f"File written to {TRAIN_DATA_FILE_PATH}/{out_file_name}")
