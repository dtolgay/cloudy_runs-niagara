# Imports 
import numpy as np
import pandas as pd
from time import time
from concurrent.futures import ProcessPoolExecutor


################################################################################
# Global variables 
#train_data_file_path = "/fs/lustre/scratch/dtolgay/cloudy_runs/z_0/cr_1_high_hden"
train_data_file_path = "/home/m/murray/dtolgay/scratch/cloudy_runs/z_0/cr_1_CO87_CII_H_O3/cr_1_CO87_CII_H_O3_metallicity_minus2_minus3point5"

centers_file_path = f"{train_data_file_path}/centers.txt"
################################################################################


# Main 
def main():
    
    print(centers_file_path)

    start = time()
    
    centers = create_df(np.loadtxt(fname=centers_file_path, skiprows=1)) 

    # centers["log_metallicity"] = np.log10(centers["metallicity"])
    # centers["log_turbulence"] = np.log10(centers["turbulence"])
    # centers["log_isrf"] = np.log10(centers["isrf"])
    # centers["log_radius"] = np.log10(centers["radius"])

    # Determine the number of nodes that is going to be used in parallel process
    max_workers = 40

    # Initiate the arrays 
    len_okay_runs = 0
    len_broken_training_data = 0
    len_not_started = 0
    len_low_hden = 0
    
    # Assuming gas_particles_df is your DataFrame and max_workers is defined
    splitted_centers_train = split_array(centers, max_workers)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit each chunk of the DataFrame to the executor
        futures = [
            executor.submit(find_situation_of_runs, chunk)
            for chunk in splitted_centers_train
        ]
    
        for future in futures:        
            result = future.result()
            len_okay_runs += result[0]
            len_broken_training_data += result[1]
            len_not_started += result[2]
            len_low_hden += result[3]

            
    print("Lengths: ")
    print(f"len_okay_runs: {len_okay_runs}")
    print(f"len_broken_training_data: {len_broken_training_data}")
    print(f"len_not_started: {len_not_started}")
    print(f"len_low_hden: {len_low_hden}")

    print(f"len(centers): {len(centers)}")
            
    end = time()

    print(f"It took {np.round(end-start, 3) / 60} minutes to run the code")

    return 0


# Functions 

# Create different chunks of of dataframe to run them parallely
def split_array(centers_train, max_workers):
    n = len(centers_train)
    chunk_size = -(
        -n // max_workers
    )  # Ceiling division to ensure all rows are included

    # Split the dataframe into chunks and store in an array
    return [centers_train[i : i + chunk_size] for i in range(0, n, chunk_size)]


def find_situation_of_runs(chunk_centers_train):
    
    
    print("I am in the function find_situation_of_runs")

    
#     okay_runs, broken_training_data, not_started, low_hden = 0, 0, 0,0
    okay_runs = []
    broken_training_data = []
    not_started = []
    low_hden = []

    i = 0
    for row, center in chunk_centers_train.iterrows():
        
        if i == 0:
            intitial_row = row

        try: 
            # fdir = f"hden{center['log_hden']:.3f}_metallicity{center['metallicity']:.3f}_turbulence{center['turbulence']:.3f}_isrf{center['isrf']:.3f}_radius{center['radius']:.3f}"
            fdir = f"hden{center['log_hden']:.5f}_metallicity{center['log_metallicity']:.5f}_turbulence{center['log_turbulence']:.5f}_isrf{center['log_isrf']:.5f}_radius{center['log_radius']:.5f}"

            if center["log_hden"] > -10: # TODO: Delete here. It is being done, because hden-4.xxx is not properly run in cloudy. nH is too low. Previously it was -3, now I changed it to be -10

                # Read the .out file to check if the run is OK
                try: 
                    with open(f"{train_data_file_path}/{fdir}/{fdir}.out", "r") as file:
                        lines = file.readlines()
                        last_line = lines[-1]    

                    if "OK" == last_line[len(last_line)-4:len(last_line)-2]:     
                        # Now you can append the new_array to your training data
                        okay_runs.append(center)

                    else:
                        broken_training_data.append(center)

                except: 
                    not_started.append(center)

            else: 
                low_hden.append(center)
        
        except Exception as e:
            print(f"Error: {e}")
        
        if ((intitial_row == 0) and (i % 1e4 == 1)):
            print(f"{i} done. {len(chunk_centers_train) - i} left")

        i += 1    
    
    len_okay_runs = len(okay_runs)
    len_broken_training_data = len(broken_training_data)
    len_not_started = len(not_started)
    len_low_hden = len(low_hden)
    
    return len_okay_runs, len_broken_training_data, len_not_started, len_low_hden


def flatten_array(array):
    flattened_array = []
    for sublist in array:
        if len(sublist) > 0:  # Check if the sublist is non-empty
            for item in sublist:
                flattened_array.append(item)
    return flattened_array


def create_df(array:np.array):
    
    # columns = [
    #     "metallicity", 
    #     "log_hden",
    #     "turbulence",
    #     "isrf",
    #     "radius"
    # ]
    
    columns = [
        "log_metallicity", 
        "log_hden",
        "log_turbulence",
        "log_isrf",
        "log_radius"
    ]    
    
    df = pd.DataFrame(array, columns=columns) 
    
    return df    


if __name__ == "__main__":
    main()