import time
import VNA_lib as vnal
import matplotlib.pyplot as plt
import numpy as np

save_path = "C:\\Users\\Administrator\\Documents\\Scripts_Commande_VNA\\CosmoCal_data\\"

vna_ip = "GPIB0::16::INSTR"  # adresse IP du VNA

vnac = vnal.VNA_commande(vna_ip)

vnac.load_calib_vna(file="wr6-5_25022026.csa")

vnac.setup_channel_vna(start_freq=110E9, stop_freq=170E9, IFBW=1000) #start_freq, stop_freq et IFBW en Hz

Sparameters=["S21", "S12", "S11", "S22"]
vnac.setup_traces(Sparameters=Sparameters)

freq_samples, mag, phi = vnac.make_one_acquisition(state_avg=False, count_avg=5, Sparameters=Sparameters)

np.save(f'{save_path}magnitude_16032026_reference_thetaR0.npy', mag)

# print(mag.shape)

### Plot
fig, axs = plt.subplots(1, 2)
axs = axs.ravel()

axs[0].plot(freq_samples, mag[2])
axs[0].set_ylabel("dB")
axs[0].set_xlabel("frequency")

axs[1].plot(freq_samples, phi[2])
axs[1].set_ylabel("deg")
axs[1].set_xlabel("frequency")

fig.tight_layout()
plt.show()

# vnac.vna.close()
# %%h
