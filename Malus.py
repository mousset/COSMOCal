import os
import time
from matplotlib import axis
import numpy as np
from datetime import datetime
import re
import glob
import csv
import data_manage_lib as dml
from astropy.io import fits


############ VNA ################
import VNA_lib as vnal
vna_ip = "GPIB0::16::INSTR"  # adresse IP du VNA.0
vnac = vnal.VNA_commande(vna_ip)

#########
#theta_r = 0 # Recepteur angle

############ SCAN PARAMETERS ################
trace_name = ["S21", "S12", "S11", "S22"] # name of the scattering parameters
state_avg = True # if True, the VNA will average over several sweeps for each position of the motor
count_avg = 10 # Number of sweeps to average
save_path = "C:\\Users\\Administrator\\Documents\\Scripts_Commande_VNA\\CosmoCal_data\\"

start_freq = 110E9 # start frequency of the VNA sweep in Hz.
stop_freq = 170E9 # stop frequency of the VNA sweep in Hz
points = 60 # number of points in the VNA sweep.
IFBW = 1000 # Hz

nS = len(trace_name) # Number of S parameters

####### VNA set-up
vnac.select_state_vna(band="WR6.5_Galaad.csa")
vnac.setup_channel_vna(start_freq=start_freq, stop_freq=stop_freq, points=points, IFBW=IFBW)
#/!\ Commencer par S21 !!!
vnac.add_trace_vna(trace_name[0], trace_number=1, window=3)
vnac.add_trace_vna(trace_name[1], trace_number=1, window=2)
vnac.add_trace_vna(trace_name[2], trace_number=1, window=1)
vnac.add_trace_vna(trace_name[3], trace_number=1, window=4)
time.sleep(1)

###### Start the scan

# Create timestamped filename for FITS file
scan_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fits_filename = f"Malus_{scan_timestamp}.fits"

# Take one acquisition
#allthetaR = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 
         #    0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, -120, -130, -140] # in degre
#allthetaR = [-60, -30, 0, 30, 60]
allthetaR = [-90, -90, -45, 0, 45, 90, 90]
nangle = len(allthetaR)
mag = np.empty((nangle, nS, points))
phi = np.empty((nangle, nS, points))
for r, thetaR in enumerate(allthetaR):
    mag[r, :, :], phi[r, :, :] = vnac.make_one_acquisition(state_avg=state_avg, count_avg=count_avg, trace_name=trace_name)
    # Save file at each step to avoid loosing data
    np.save(f'{save_path}mag.npy', mag)
    np.save(f'{save_path}phi.npy', phi)
    print(f"thetaR {thetaR}° DONE - Go to the next")
    input()
    print("Continuing execution...")

# Also save to FITS format with header
header_info = {
    'THETA_R': str(allthetaR),
    'START_FRQ': start_freq,
    'STOP_FRQ': stop_freq,
    'POINTS': points,
    'IFBW': IFBW,
    'TRACES': ', '.join(trace_name),
    'TIMESTAMP': datetime.now().isoformat()
}
dml.save_measurement_to_fits(mag, phi, save_path, 
                                filename=fits_filename, header_info=header_info)

####### Close hardware connexions
vnac.vna.close()
print("Mesures terminées\nConnexions fermées")