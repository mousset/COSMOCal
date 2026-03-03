"""
Author : Louise Mousset
Date : 19/01/2026
"""

import pyvisa
import time
import numpy as np

### Standard Commands for Programmable Instruments (SCPI) are used to control the VNA.
### SCPI is not case sensitive
### Shortcuts :
# *IDN? : ask the identification of the instrument
# AVER = average
# BAND = bandwidth
# CALC = calculate
# DEL = delete
# DEF = define
# DIS = display
# FEED = feed
# FORM = 
# FPR = preset
# FREQ = frequency
# IMM = immediate
# INIT = initiate
# MEAS = measure
# MMEM = memory
# OFFS = offset
# PAR = parameter
# POIN = points
# SEL = select
# STAT = state
# SWE = sweep
# SYST = system
# TRAC = trace
# WAI = wait
# WIND = window


class VNA_commande:

    def __init__(self, ip_adress_vna):
        """
        Establishes communication with the VNA using VISA addresses.
        It also prints the identification strings of each device.

        Parameters
        ----------
        ip_address_vna : string
            Ip address of the VNA.

        Returns
        -------
        None.

        """
        try:
            rm = pyvisa.ResourceManager()
            self.vna = rm.open_resource(f'{ip_adress_vna}')
            self.vna.timeout = 30000  # timeout of 30 sec
            print("Connecté à :", self.vna.query("*IDN?")) # ask identification
        except Exception as e:
            print(f"erreur lors de l'initialisation du VNA: {e}")

    def load_calib_vna(self, file="WR6.5_Galaad.csa"):
        """
        Loads a saved VNA measurement state.
        Be sure to use only measurement state files named "WR.<x>_Galaad.csa" (for example:
        WR6.5_Galaad.csa)

        Parameters
        ----------
        band : string
            Name of the band that has to be loaded. The default is "WR6.5_Galaad.csa".

        Returns
        -------
        None.

        """
        try:
            self.vna.write(':MMEM:LOAD:FILE "%s"' % (f'D:/{file}')) # call the saved state and calset data 
            print(f'VNA state {file} loaded.')
            time.sleep(2)
        except Exception as e:
            print(f"erreur lors de la selection de la bande: {e}")

    def setup_channel_vna(self, start_freq=1E9, stop_freq=3E9, points=201, IFBW=1000): 
        """
        Configures a VNA channel.

        Parameters
        ----------
        start_freq : integer or floating
            Start frequency (in Hz) of the sweep. The default is 1E9.
        stop_freq : integer or floating
            Stop frequency (in Hz) of the sweep. The default is 3E9.
        points : integer
            Number of points/frequency in the frequency sweep. The default is 201.
        IFBW : integer or floating
            Bandwidth (in Hz) of the low-pass filter at the mixer output, before detection. The default is 1000.

        Returns
        -------
        None.

        """
        try:
            channel = 1
            # Delete all previous parameters
            #self.vna.write(f'CALC{channel}:PAR:DEL:ALL') 

            ## Set the start and stop frequencies, number of points, IFBW
            self.vna.write(f'SENS{channel}:FREQ:START {start_freq}') 
            self.vna.write(f'SENS{channel}:FREQ:STOP {stop_freq}') 
            self.vna.write(f'SENS{channel}:SWE:POIN {points}')
            self.vna.write(f'SENS{channel}:BAND {IFBW}')
            print(f"Canal {channel} configuré : start={start_freq}, stop={stop_freq}, points={points}")

            ## Turn off the continuous measure mode => avoid Error 213 (Init ignored)
            self.vna.write(f'INIT{channel}:CONT OFF') 
            print("Continuous mode OFF")
            time.sleep(1)

            ### delete all the default measurements
            self.vna.write("CALC1:MEAS:DEL:ALL") 
            print("All measurements deleted")
            time.sleep(1)

        except Exception as e:
            print(f"erreur lors du stetup du cannal de mesure: {e}")

    
    # def setup_traces(self, Sparameters = ["S21", "S12", "S11", "S22"]):
    #     nS = len(Sparameters)
    #     ### delete all the default measurements
    #     self.vna.write("CALC1:MEAS:DEL:ALL") 
        
    #     for i in range(nS):
    #         trace_name = Sparameters[i]
    #         # Create a measurement for the S parameter
    #         self.vna.write(f"CALC1:MEAS{i+1}:DEF '{trace_name}'")

    #         # Displays each measurement in a different window
    #         # It assigns the next available trace number to the measurement
    #         self.vna.write(f"DISP:MEAS{i+1}:FEED {i+1}")

    #     time.sleep(3) # Give it some time 
    #     # Autoscale all traces in each window
    #     for i in range(nS): 
    #         self.vna.write(f"DISP:WIND{i+1}:Y:AUTO")

    #     return
    
    def setup_traces(self, Sparameters=["S21", "S12", "S11", "S22"]):
        """
        Adds and displays a new measurement trace on the VNA.

        Parameters
        ----------
        trace_name : string
            Name of the scattering parameter. The default is "S21".
        trace_number : integer
            Number of the trace to be displayed (trace_number ∈ [1,4]). The default is 1.
        window : integer
            Number of the window you want the trace to be displayed in (window ∈
            [1,4]). The default is 1.

        Returns
        -------
        None.

        """
          
        try: 
            channel = 1
            trace = 1
            for i, Sparam in enumerate(Sparameters):
                self.vna.write(f'CALC{channel}:PAR:DEF'+' '+f"{Sparam}"+","+f'{Sparam}') # define a new trace
                self.vna.write(f'CALC{channel}:PAR:SEL "{Sparam}"') # select the new trace
                self.vna.write(f'DISP:WIND{i+1}:STAT ON') # turn on the window display
                self.vna.write(f'DISP:WIND{i+1}:TRAC{trace}:FEED "{Sparam}"') # put the new trace into the window
                print(f"Trace {Sparam} ajoutée à la fenêtre {i+1}")
            time.sleep(3)
            # Autoscale all traces in each window
            for i, Sparam in enumerate(Sparameters):
                self.vna.write(f':DISP:WIND{i+1}:Y:AUTO') # autoscale the trace
            time.sleep(1)

        except Exception as e:
            print(f"erreur lors de l'ajout de la trace: {e}")

    def log_error(self):
        """
        Prints the current system error from the VNA (useful for debugging).

        Returns
        -------
        None.

        """
        self.vna.write("SYST:ERR?")
        err = self.vna.read()
        print(f'VNA ERROR: {err}')

    def ask_frequency_range(self):
        channel = 1
        ## Ask start and stop frequencies and number of points to the VNA
        start_freq = float(self.vna.query(f'SENS{channel}:FREQ:START?')) 
        stop_freq = float(self.vna.query(f'SENS{channel}:FREQ:STOP?'))
        points = int(self.vna.query(f'SENS{channel}:SWE:POIN?'))
        if start_freq == stop_freq:
            self.vna.write(f'SENS{channel}:SWE:POIN 1') # set the number of point to 1
            print("Balayage mono-fréquence:")
        return start_freq, stop_freq, points
    
    def make_one_acquisition(self, state_avg=True, count_avg=5, Sparameters=["S12"]):
        """      
        state_avg: If True, perform an average on several measurement at each frequency sample
        count_avg: number of measurement on which the average is performed

        """
        channel = 1
        #turn off and on the averaging before tacking the measurement to make sure the averaging is done at a given position
        if state_avg:
            self.vna.write(f'SENS{channel}:AVER OFF')
            time.sleep(0.1)
            self.vna.write(f'SENS{channel}:AVER ON')
            time.sleep(1)
            self.vna.write(f'SENS{channel}:AVER:COUNT {count_avg}') # set the average count to count_avg
            for z in range(count_avg): # take count_avg measures to correctly average the signals
                self.vna.write(f'INIT{channel}:IMM')
                self.vna.write('*WAI')
        else:
            self.vna.write(f'SENS{channel}:AVER OFF')
            self.vna.write(f'INIT{channel}:IMM')
            self.vna.write('*WAI')

        freq_samples = self.vna.query_ascii_values("CALC1:MEAS1:X:VAL?")

        all_magnitudes = []
        all_phases = []
        for i, trace in enumerate(Sparameters):
            print(f'Measuring {trace}')
            # Select the S-parameter
            self.vna.write(f'CALC{channel}:PAR:SEL {trace}')
            time.sleep(2)

            # Get the magnitude
            # 'FDATA' -> real part of the data
            self.vna.write(f'CALC{channel}:FORM MLOG') # magnitude (dB)
            all_magnitudes.append(self.vna.query_ascii_values(f'CALC{channel}:DATA? FDATA'))
            time.sleep(2)

            # Get the phase
            self.vna.write(f'CALC{channel}:FORM PHAS') # phase (°)
            all_phases.append(self.vna.query_ascii_values(f'CALC{channel}:DATA? FDATA'))
            time.sleep(2)
        
        return np.array(freq_samples), np.array(all_magnitudes), np.array(all_phases)

