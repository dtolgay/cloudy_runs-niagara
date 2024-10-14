# Functions
import numpy as np 
import pandas as pd 
import os 


##########################################################################################################################################################################################
# Main 

def main(fdir, verbose):

    # Read file 
    centers = create_df(np.loadtxt(fname=f"{fdir}/centers.txt")) 

    # Defining run specifications
    redshift = 3.0
    cosmic_ray = 1.0

    #################### Create .in files
    for row, center in centers.iterrows():


        directory_name = f"hden{center['log_hden']:.5f}_metallicity{center['log_metallicity']:.5f}_turbulence{center['log_turbulence']:.5f}_isrf{center['log_isrf']:.5f}_radius{center['log_radius']:.5f}"
        
        file_name = f"{fdir}/{directory_name}/{directory_name}.in"

        # Print directory and file names (optional)
    #     print(f"\ndirectory_name: {directory_name}\n")
    #     print(f"filename: {file_name}\n")

        # Create the directory
        try:
            os.makedirs(f"{fdir}/{directory_name}", mode=0o777)  # 0777 permission in Python

            create_in_file(
                file_name = file_name, 
                center = center, 
                redshift = redshift, 
                cosmic_ray = cosmic_ray
            )

            if row % 1e4 == 1:
                print(f"{row} finished. Left {len(centers) - row}")            
                print(f"Directory {directory_name} created!\n")            
            
        except FileExistsError:
            if (verbose): print(f"Directory {directory_name} already exists. Only checking to create .in file. \n")

            # Check if file exits.
            if not os.path.isfile(file_name): 
                create_in_file(
                    file_name = file_name, 
                    center = center, 
                    redshift = redshift, 
                    cosmic_ray = cosmic_ray
                )
            else: # File exists. Do not create new.
                if (verbose): print(f".in file exists: {directory_name}.\n")
                pass

        except Exception as e:
            if (verbose): print(f"Unable to create directory: {directory_name}. Error: {e}\n")
            pass
            # Break from the program or handle the error    


    return 0 


##########################################################################################################################################################################################
# Functions 

def create_df(array:np.array):
    
    columns = [
        "log_metallicity", 
        "log_hden",
        "log_turbulence",
        "log_isrf",
        "log_radius",
    ]
    
    df = pd.DataFrame(array, columns=columns) 
    
    return df



def create_in_file(file_name, center, redshift, cosmic_ray):
    
    log_hden = "{:.5f}".format(center["log_hden"])
    log_metallicity = "{:.5f}".format(center["log_metallicity"])
    log_turbulence = "{:.5f}".format(center["log_turbulence"])
    log_isrf = "{:.5f}".format(center["log_isrf"])
    log_radius = "{:.5f}".format(center["log_radius"])
    
    try:
        with open(file_name, "w") as fp:
            fp.write("title Parallel Plane Slab DT\n")
            fp.write("set nend 4000\n")  # Set number limiting number of zones.
            fp.write(f"table ISM factor {log_isrf} log\n")
            fp.write("radius 30\n")
            fp.write(f"hden {log_hden} log\n")
            fp.write(f"CMB, z={redshift:.5f}\n")
            fp.write("abundances ISM\n")
            fp.write(f"metals and grains {log_metallicity} log\n")
            fp.write(f"turbulence {log_turbulence} km/sec log\n")
            fp.write(f"cosmic rays background {cosmic_ray:.3f} linear\n")
            fp.write(f"stop thickness {log_radius} log parsec\n")  # This sets the stopping radius
            fp.write("stop temperature off\n")
            # fp.write("iterate\n")  # iterate to converge option might be better
            fp.write("iterate to converge\n")
            fp.write("print line sort intensity\n")
            # fp.write("element carbon isotopes (12, 5) (13, 1)\n")
            fp.write("save lines, emissivity, \"_em.str\"\n")
            fp.write("H  1 1215.67 # Lya\n")
            fp.write("H  1 6562.80 # Ha\n")
            fp.write("H  1 4861.32 # Hb\n")
            fp.write("CO  2600.05m # CO(1-0)\n")
            fp.write("CO  1300.05m # CO(2-1)\n")
            fp.write("CO  866.727m # CO(3-2)\n")
            fp.write("CO  650.074m # CO(4-3)\n")
            fp.write("CO  520.089m # CO(5-4)\n")
            fp.write("CO  433.438m # CO(6-5)\n")
            fp.write("CO  371.549m # CO(7-6)\n")
            fp.write("CO  325.137m # CO(8-7)\n")
            fp.write("\"^13CO\" 2719.67m\n")
            fp.write("C  2 157.636m\n")
            fp.write("O  3 88.3323m\n")
            fp.write("O  3 5006.84 # wavelength in Angstrom\n")
            fp.write("O  3 4958.91 # wavelength in Angstrom\n")
            fp.write("end of lines\n")
            fp.write("save lines, array, \".lines\"\n")
            fp.write("save grain abundance \".gbu\"\n")
            fp.write("save performance \".per\"\n")
            fp.write("save overveiw last \".ovr\"\n")
            fp.write("save monitors last \".asr\"\n")
            fp.write("save temperature last \".tem\"\n")
            fp.write("save overview \".ovr1\"\n")
            fp.write("save molecules last \".mol\"\n")
            fp.write("save molecules \".mol1\"\n")
            fp.write("save heating \".het\"\n")
            fp.write("save cooling \".col\" # Column densities\n")
            fp.write("save dr last \".dr\"\n")
            fp.write("save results last \".rlt\"\n")
            fp.write("save continuum last \".con\" units microns\n")
            fp.write("Save line labels [long] [no index] \".labels\"\n")
            fp.write("print line optical depths \".tau\"\n")

        # print(f"File {file_name} created!")

    except IOError as e:
        print(f"Error opening file: {e}")


##########################################################################################################################################################################################

if __name__ == "__main__":

    # CITA clusters
    # fdir = "/fs/lustre/scratch/dtolgay/cloudy_runs/z_0/trial"

    # Niagara clusters
    fdir = "/scratch/m/murray/dtolgay/cloudy_runs/z_0/cr_1_CO87_CII_H_O3/cr_1_CO87_CII_H_O3_metallicity_above_minus_2"

    main(fdir=fdir, verbose=False)