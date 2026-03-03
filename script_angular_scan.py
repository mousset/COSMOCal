import os
import time
import numpy as np
from datetime import datetime
import re
import glob
import csv
import data_manage_lib as dml
from astropy.io import fits

# TODO : clarifier un peu le script mais il marche

############ ESP ################
import ESP_lib as espl
motor_controller_ip_ang = "GPIB0::2::INSTR" # Angular scan 
espc = espl.ESP_commande(motor_controller_ip_ang)

############ VNA ################
import VNA_lib as vnal
vna_ip = "GPIB0::16::INSTR"  # adresse IP du VNA.0
vnac = vnal.VNA_commande(vna_ip)

############ SCAN PARAMETERS ################
accel = "10"
deccel = "10"
speed = 1
Sparameters = ["S21", "S12", "S11", "S22"] # name of the scattering parameters
axis = 1 # number of the ESP axis
units = 7
alpha_min, alpha_max = 0, 380 # limits of the angular scan in degrees
sens = "-to+" # direction of the scan; -to+ for the scan to begin at alpha_min and end at alpha_max, and +to- for the scan to begin at alpha_max and end at alpha_min
pas = 10 # steps
state_avg = True # if True, the VNA will average over several sweeps for each position of the motor
count_avg = 10 # Number of sweeps to average
save_path = "C:\\Users\\Administrator\\Documents\\Scripts_Commande_VNA\\CosmoCal_data\\"

start_freq = 110E9 # start frequency of the VNA sweep in Hz.
stop_freq = 170E9 # stop frequency of the VNA sweep in Hz
points = 60 # number of points in the VNA sweep.
IFBW = 1000 # Hz

theta_R = 90 # angle of the receiver in degrees

unit_name = espc.give_unit_name(units)
nS = len(Sparameters) # Number of S parameters

####### VNA set-up
vnac.load_calib_vna(file="wr6-5_25022026.csa")
vnac.setup_channel_vna(start_freq=start_freq, stop_freq=stop_freq, points=points, IFBW=IFBW)
vnac.setup_traces(Sparameters=Sparameters)

######## Move to initial position
#####  give parameters to the axis (acceleration, speed mode...)
espc.setup_axis_parameters(axis=axis, units=units, speed=speed, accel=accel, deccel=deccel)
time.sleep(2)
if sens == '-to+':
    pas = abs(pas)
    start_movement = alpha_min
elif sens == '+to-':
    pas = -abs(pas)
    start_movement = -alpha_min
print(f'\n Going to start position {start_movement}{unit_name}')
espc.move(axis=axis, movement=start_movement, absolute=True)
time.sleep(5)

########## GET VNA frequency range
# Useless for now 
#start_freq, stop_freq, points = vnac.ask_frequency_range()
#alpha_val = np.arange(alpha_min, alpha_max + pas, pas)

###### Start the scan
nstep = int(np.ceil(np.abs(1 + (alpha_max - alpha_min) / pas )))
print(f'\nTotal number of steps {nstep}')

# Create timestamped filename for FITS file
scan_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fits_filename = f"Scan_{scan_timestamp}.fits"

freq_samples = np.empty(points)
mag = np.empty((nstep, nS, points))
phi = np.empty((nstep, nS, points))
for i in range(nstep):
    print(f'\nStep number {i+1}/{nstep}')
    # Take one acquisition
    freq_samples, mag[i, :, :], phi[i, :, :] = vnac.make_one_acquisition(state_avg=state_avg, count_avg=count_avg, Sparameters=Sparameters)
    print(f'Magnitudes {mag.shape}:') # [nS, points]
    print(f'Phases: {phi.shape}')
    # Move by one step
    espc.move(axis=axis, movement=pas, absolute=False)
    time.sleep(2)
    # Save file at each step to avoid loosing data
    np.save(f'{save_path}mag.npy', mag)
    np.save(f'{save_path}phi.npy', phi)
    
    # Also save to FITS format with header
    header_info = {
        'THETA_R': theta_R,
        'START_FRQ': start_freq,
        'STOP_FRQ': stop_freq,
        'POINTS': points,
        'STATE_AVG': state_avg,
        'COUNT_AVG': count_avg,
        'IFBW': IFBW,
        'TRACES': ', '.join(Sparameters),
        'ALPH_MI': alpha_min,
        'ALPH_MA': alpha_max,
        'STEP': pas,
        'NSTEPS': nstep,
        'CURRENT_S': i + 1,
        'TIMESTAMP': datetime.now().isoformat()
    }
    dml.save_measurement_to_fits(freq_samples, mag[:i+1, :, :], phi[:i+1, :, :], save_path, 
                                  filename=fits_filename, header_info=header_info)

####### Close hardware connexions
espc.return_home(axis=axis)
vnac.vna.close()
espc.esp.close()
print("Mesures terminées\nConnexions fermées")

