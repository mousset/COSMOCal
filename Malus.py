import numpy as np
from datetime import datetime
import data_manage_lib as dml


############ VNA ################
import VNA_lib as vnal
vna_ip = "GPIB0::16::INSTR"  # adresse IP du VNA.0
vnac = vnal.VNA_commande(vna_ip)

############ SCAN PARAMETERS ################
Sparameters = ["S21", "S12", "S11", "S22"] # name of the scattering parameters
state_avg = True # if True, the VNA will average over several sweeps for each position of the motor
count_avg = 2 # Number of sweeps to average
save_path = "C:\\Users\\Administrator\\Documents\\Scripts_Commande_VNA\\CosmoCal_data\\"

start_freq = 110E9 # start frequency of the VNA sweep in Hz.
stop_freq = 170E9 # stop frequency of the VNA sweep in Hz
IFBW = 1000 # Hz

nS = len(Sparameters) # Number of S parameters

####### VNA set-up
vnac.load_calib_vna(file="wr6-5_25022026.csa")
vnac.setup_channel_vna(start_freq=start_freq, stop_freq=stop_freq, IFBW=IFBW)
vnac.setup_traces(Sparameters=Sparameters)

start_freq, stop_freq, points = vnac.ask_frequency_range()

###### Start the scan

# Create timestamped filename for FITS file
scan_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fits_filename = f"Malus_{scan_timestamp}.fits"

# Take acquitions for all angles of the polarizer
allthetaR = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 
             0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, -120] # in degrees
#allthetaR = [-60, -30, 0, 30, 60]
#allthetaR = [-90, -45, 0, 45, 90]
nangle = len(allthetaR)
mag = np.empty((nangle, nS, points))
phi = np.empty((nangle, nS, points))
for r, thetaR in enumerate(allthetaR):
    freq_samples, mag[r, :, :], phi[r, :, :] = vnac.make_one_acquisition(state_avg=state_avg, count_avg=count_avg, Sparameters=Sparameters)
    # Save file at each step to avoid loosing data
    #np.save(f'{save_path}mag.npy', mag)
    #np.save(f'{save_path}phi.npy', phi)
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
    'TRACES': ', '.join(Sparameters),
    'TIMESTAMP': datetime.now().isoformat()
}
dml.save_measurement_to_fits(freq_samples, mag, phi, save_path, 
                                filename=fits_filename, header_info=header_info)

####### Close hardware connexions
vnac.vna.close()
print("Mesures terminées\nConnexions fermées")