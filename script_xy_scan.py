import os
import time
import numpy as np
from datetime import datetime
import re
import glob
import csv

# TODO Refaire ce script de la même façon que script_angular_scan.py
# Pour le moment c'est un copié-collé du script de Galaad 

def boustrophedon(A,B,pas_x,pas_y):
    """
    Generates the list of coordinates (x, y) for a boustrophedon path
    covering the entire grid defined by points A and B
    and the given step.

    Parameters
    ----------
    A : array of integer or array of floating
        Start coordinates of the scan.
    B : array of integer or array of floating
        End coordinates of the scan..
    pas_x : integer or floating
        Step size of the x-axis.
    pas_y : integer or floating
        Step size of the y-axis. 
    
    Returns
    -------
    parcours_full_grid : array
        A list of tuples (x, y) representing the positions to be traversed
        in boustrophedon order, covering the entire grid.
    """
    xi, yi = A
    xf, yf = B
    min_x = min(xi, xf)
    max_x = max(xi, xf)
    min_y = min(yi, yf)
    max_y = max(yi, yf)
    num_points_x = int(round((max_x - min_x) / pas_x + 1))
    num_points_y = int(round((max_y - min_y) / pas_y + 1))
    x_coords_full = np.linspace(min_x, max_x, num_points_x)
    y_coords_full = np.linspace(min_y, max_y, num_points_y)
    parcours_full_grid = []
    start_left_to_right = True 
    for i, y in enumerate(y_coords_full):
        if (start_left_to_right and i % 2 == 0) or (not start_left_to_right and i % 2 != 0):
            for x in x_coords_full:
                pos = (x, y)
                parcours_full_grid.append(pos)
        else:
            for x in reversed(x_coords_full):
                pos = (x, y)
                parcours_full_grid.append(pos)
    return parcours_full_grid

def balayage_2D(self, trace_name=["S12","S21","S11","S22"], axis=[2,3], units=2, A=[0,0], B=[5,5], pas_axe1=1, pas_axe2=1, state_avg=True, count_avg=5, save_path="C:\\Users\\Thomas\\Documents\\Galaad_B\\vna_data_test_galaad", note="", File_name="Compilation"):
        """
        Performs a full 2D scan between two spatial points A and B.
        The scan will begin at point A and end at point B. It will take measures at every step.

        Parameters
        ----------
        trace_name : array of string
            List of S-parameters . The default is ["S12","S21","S11","S22"].
        axis : array of integer
            List of the ESP axis. The default is [2,3].
        units : integer
            The unit of the movement (0 = encoder count, 1 = motor step, 2 = millimeter,
            3 = micrometer, 4 = inches, 5 = milli-inches, 6 = micro-inches, 7 = degree, 8 = gradient,
            9 = radian, 10 = milliradian, 11 = microradian). The default is 2.
        A : array of integer or array of floating
            Start coordinates of the scan. The default is [0,0].
        B : array of integer or array of floating
            End coordinates of the scan. The default is [5,5].
        pas_axe1 : integer or floating
            Step size of the axis 1. The default is 1.
        pas_axe2 : integer or floating
            Step size of the axis 2. The default is 1.
        state_avg : boolean
            If True the averaging will be on, if false it will be off. The default is True.
        count_avg : integer
            The number of measures to average on. The default is 5.
        save_path : string
            Output directory path. The default is "C:\\Users\\Thomas\\Documents\\Galaad_B\\vna_data_test_galaad".
        note : string
            Optional annotation. The default is "".
        File_name : string
            Name of the final files returned by the script. The default is "Compilation".

        Returns
        -------
        None.

        """
        try:
            ################################################################################################
            # parameters
            ################################################################################################
            channel=1
            accel="5"
            deccel="5"
            speed=3
            self.esp.write_termination = '\r'
            self.esp.read_termination = '\r'
            ################################################################################################
            # give parameters to the axis (acceleration, speed mode...)
            ################################################################################################
            for axe in axis:
                self.esp.write(f'{axe}MO') # turn on the axis
                self.esp.write(f'{axe}SN{units}') # set the unit of the axis: 0 = encoder count, 1 = motor step, 2 = millimeter, 3 = micrometer, 4 = inches, 5 = milli-inches, 6 = micro-inches, 7 = degree, 8 = gradient, 9 = radian, 10 = milliradian, 11 = microradian
                self.esp.write(f'{axe}AC{accel}') # set the axis acceleration
                self.esp.write(f'{axe}AG{deccel}') # set the axis decceleration
                if speed==1:
                    speed_mode = "JW5" # slow
                elif speed==2:
                    speed_mode = "JH10" # medium
                elif speed==3:
                    speed_mode = "VU15" # fast
                self.esp.write(f'{axe}{speed_mode}') # set the speed mode
            ################################################################################################
            # sweep spacial parameters
            ################################################################################################
            self.esp.write(f'{axis[0]}PA{A[0]}')
            self.esp.write(f'{axis[0]}WS')
            self.esp.write(f'{axis[1]}PA{A[1]}')
            self.esp.write(f'{axis[1]}WS')
            L_tot_1 = int(np.round((B[0]-A[0])/pas_axe1,0))
            L_tot_2 = int(np.round((B[1]-A[1])/pas_axe2 + 1,0))
            nb_tot_position = int(np.ceil(((1 + (B[0]-A[0]) / pas_axe1 ))*(1 + (B[1]-A[1]) / pas_axe2 )))
            time.sleep(2)
            start_freq = float(self.vna.query(f'SENSe{channel}:FREQuency:STARt?')) # ask the vna the value of start_freq
            stop_freq = float(self.vna.query(f'SENSe{channel}:FREQuency:STOP?')) # ask the vna the value of stop_freq
            points = int(self.vna.query(f'SENSe{channel}:SWEep:POINts?')) # ask the vna the number of point
            if start_freq == stop_freq:
                self.vna.write(f'SENSe{channel}:SWEep:POINts 1') # set the number of point to 1
                print("Balayage mono-fréquence:")
            hh = 1 # hh tracks the number of measurements
            parcours = boustrophedon(A, B, pas_axe1, pas_axe2)
            x_val = [float(p[0]) for p in parcours]
            y_val = [float(p[1]) for p in parcours]
            unit = {0:"encoder_count", 1:"motor_step", 2:"mm", 3:"µm", 4:"inches", 5:"milli-inches", 6:"micro-inches", 7:"deg", 8:"grad", 9:"rad", 10:"mili-rad", 11:"µ-rad"}[int(units)]
            ################################################################################################
            # preset file creation
            ################################################################################################  
            file_name = f"{File_name}_parameters.txt"
            os.makedirs(save_path, exist_ok=True)    
            full_path = os.path.join(save_path, file_name)
            with open(full_path, 'w') as f:
                header = ["start_freq (Hz)", "stop_freq (Hz)", "number_of_point", "average", f"step_x ({unit})", f"step_y ({unit})", f"x_min ({unit})", f"x_max ({unit})", f"y_min ({unit})", f"y_max ({unit})"]
                f.write("\t".join(header) + "\n")
                if state_avg:
                    line = [f"{start_freq}",  f"{stop_freq}", f"{points}", f"{count_avg}", f"{pas_axe1}", f"{pas_axe2}", f"{A[0]}", f"{B[0]}", f"{A[1]}", f"{B[1]}"]
                else: 
                    line = [f"{start_freq}",  f"{stop_freq}", f"{points}", "0", f"{pas_axe1}", f"{pas_axe1}", f"{A[0]}", f"{B[0]}", f"{A[1]}", f"{B[1]}"]
                f.write("\t".join(line) + "\n")
            ################################################################################################
            # this is the 2D-sweeping script 
            ################################################################################################
            for axe in axis:
                self.esp.write(f'{axe}MO')
            for i in range(L_tot_2):
                for j in range(L_tot_1):
                    ite_start_time = time.time()
                    if i%2 ==0:
                        signe = "+" # change sign to make the arm go back and forth
                    else:
                        signe = "-"
                    time.sleep(2)   
                    if state_avg: # if state_avg=True: turn off and on the averaging before tacking the measure to make sure the averaging is done at a given position 
                        self.vna.write(f'SENSe{channel}:AVERage OFF')
                        time.sleep(0.1)
                        self.vna.write(f'SENSe{channel}:AVERage ON')
                        time.sleep(1)
                        self.vna.write(f'SENSe{channel}:AVERage:COUNt {count_avg}') # set the average count to count_avg
                        for z in range(count_avg): # take count_avg measures to correctly average the signals
                            self.vna.write(f'INITiate{channel}:IMMediate')
                            self.vna.write('*WAI')
                    else: 
                        self.esp.write(f'{axis[0]}WS')
                        self.esp.write(f'{axis[1]}WS')
                        self.vna.write(f'SENSe{channel}:AVERage OFF')
                        self.vna.write(f'INITiate{channel}:IMMediate')
                        self.vna.write('*WAI')
            ################################################################################################
            # Saving in a file
            ################################################################################################
                    all_magnitudes = []
                    all_phases = []
                    freq_data = np.linspace(start_freq, stop_freq, points)
                    for trace in trace_name:
                        self.vna.write(f'CALCulate{channel}:PARameter:SELect "{trace}"')
                        time.sleep(1)
                        self.vna.write(f'CALCulate{channel}:FORMat MLOG') # magnitude (dB)
                        time.sleep(1)
                        mag_data = self.vna.query_ascii_values(f'CALCulate{channel}:DATA? FDATA') # 'FDATA' -> real part of the data
                        self.vna.write(f'CALCulate{channel}:FORMat PHAS') # phase (°)
                        time.sleep(1)
                        phase_data = self.vna.query_ascii_values(f'CALCulate{channel}:DATA? FDATA')
                        all_magnitudes.append(mag_data)
                        all_phases.append(phase_data)
                    date = datetime.now().strftime("%m-%d-%Y")
                    file_name = f"Balayage_{hh}.txt"
                    os.makedirs(save_path, exist_ok=True)
                    full_path = os.path.join(save_path, file_name)
                    with open(full_path, 'w') as f:
                        header = ["Frequency (Hz)"]
                        for trace in trace_name:
                            header.append(f"Magnitude_{trace}")
                            header.append(f"Phase_{trace}")
                        if state_avg:
                            header.append(f'{date}_{trace_name}_strat={start_freq/1E9}GHz_strop={stop_freq/1E9}GHz_average={count_avg}_[x_y]=[{x_val[hh-1]}_{y_val[hh-1]}]')
                        else:
                            header.append(f'{date}_{trace_name}_strat={start_freq/1E9}GHz_strop={stop_freq/1E9}GHz_avrage=False_[x_y]=[{x_val[hh-1]}_{y_val[hh-1]}]')
                        header.append(f'note=[{note}]')
                        f.write("\t".join(header) + "\n")
                        for l in range(points):
                            line = [f"{freq_data[l]:.2f}"]
                            for mag, phase in zip(all_magnitudes, all_phases):
                                line.append(f"{mag[l]:.4f}")
                                line.append(f"{phase[l]:.4f}")
                            f.write("\t".join(line) + "\n")
                    print(f"Mesure {hh}/{int(nb_tot_position)}")
                    self.esp.write(f'{axis[0]}PR{signe}{str(pas_axe1)}') # move the axis 1
                    self.esp.write(f'{axis[0]}WS')            
                    hh = hh+1
                    ite_end_time = time.time()
                    time_meas = ite_end_time - ite_start_time
                    if i==0 and j==0:
                        print(f"Temps estimé pour le scan: {np.round(time_meas*nb_tot_position/3600,2)}h")
                if hh>nb_tot_position: # avoid making too much measurement
                    break
                if state_avg: # if state_avg=True: turn off and on the averaging before tacking the measure to make sure the averaging is done at a given position 
                    self.vna.write(f'SENSe{channel}:AVERage OFF')
                    time.sleep(0.1)
                    self.vna.write(f'SENSe{channel}:AVERage ON')
                    self.vna.write(f'SENSe{channel}:AVERage:COUNt {count_avg}') # set the average count to count_avg
                    for z in range(count_avg): # take count_avg measures to correctly average the signals
                        self.vna.write(f'INITiate{channel}:IMMediate')
                        self.vna.write('*WAI') 
                else: 
                    self.vna.write(f'SENSe{channel}:AVERage OFF')
                    self.vna.write(f'INITiate{channel}:IMMediate')
                    self.vna.write('*WAI') 
            ################################################################################################
            # Saving in a file (for each value j we save and for each value i we also save after the j-loop)
            ################################################################################################
                all_magnitudes = []
                all_phases = []
                start_freq = float(self.vna.query(f'SENSe{channel}:FREQuency:STARt?')) # ask the vna the value of start_freq
                stop_freq = float(self.vna.query(f'SENSe{channel}:FREQuency:STOP?')) # ask the vna the value of stop_freq
                points = int(self.vna.query(f'SENSe{channel}:SWEep:POINts?')) # ask the vna the number of point
                freq_data = np.linspace(start_freq, stop_freq, points)
                for trace in trace_name:
                    self.vna.write(f'CALCulate{channel}:PARameter:SELect "{trace}"')
                    time.sleep(1)
                    self.vna.write(f'CALCulate{channel}:FORMat MLOG') # magnitude (dB)
                    time.sleep(1)
                    mag_data = self.vna.query_ascii_values(f'CALCulate{channel}:DATA? FDATA') # 'FDATA' -> real part of the data
                    self.vna.write(f'CALCulate{channel}:FORMat PHAS') # phase (°)
                    time.sleep(1)
                    phase_data = self.vna.query_ascii_values(f'CALCulate{channel}:DATA? FDATA')
                    all_magnitudes.append(mag_data)
                    all_phases.append(phase_data)
                date = datetime.now().strftime("%m-%d-%Y")
                file_name = f"Balayage_{hh}.txt"
                os.makedirs(save_path, exist_ok=True)
                full_path = os.path.join(save_path, file_name)
                with open(full_path, 'w') as f:
                    header = ["Frequency (Hz)"]
                    for trace in trace_name:
                        header.append(f"Magnitude_{trace}")
                        header.append(f"Phase_{trace}")
                    if state_avg:
                        header.append(f'{date}_{trace_name}_strat={start_freq/1E9}GHz_strop={stop_freq/1E9}GHz_average={count_avg}_[{x_val[hh-1]}_{y_val[hh-1]}]')
                    else:
                        header.append(f'{date}_{trace_name}_strat={start_freq/1E9}GHz_strop={stop_freq/1E9}GHz_[x_y]=[{x_val[hh-1]}_{y_val[hh-1]}]')
                    header.append(f'note=[{note}]')
                    f.write("\t".join(header) + "\n")
                    for l in range(points):
                        line = [f"{freq_data[l]:.2f}"]
                        for mag, phase in zip(all_magnitudes, all_phases):
                            line.append(f"{mag[l]:.4f}")
                            line.append(f"{phase[l]:.4f}")
                        f.write("\t".join(line) + "\n")
                print(f"Mesure {hh}/{int(nb_tot_position)}")
                hh = hh+1
                self.esp.write(f'{axis[1]}PR{str(pas_axe2)}') # when the axis 1 is at B[0] we need the axis 2 to move
                self.esp.write(f'{axis[1]}WS')
            ################################################################################################
            # one file to rule them all (create a final data file at the end of the acquisition to compile the data at a given frequency)
            ################################################################################################  
            for freq_idx in range(points):
                target_frequency = freq_data[freq_idx]
                ligne_freq = freq_idx + 1
                file_name = f"{File_name}_{target_frequency/1E9:.3f}GHz.txt"
                full_path = os.path.join(save_path, file_name)
                all_mag = []
                all_phase = []
                for i, trace in enumerate(trace_name):
                    mag_col = 1 + 2 * i      
                    phase_col = mag_col + 1
                    magnitudes = file_to_array(save_path, ligne_freq, mag_col)
                    phases = file_to_array(save_path, ligne_freq, phase_col)
                    all_mag.append(magnitudes)
                    all_phase.append(phases)
                with open(full_path, 'w') as f:
                    header = ["x", "y"]
                    for trace in trace_name:
                        header.extend([f"Magnitude_{trace}", f"Phase_{trace}"])
                    if state_avg:
                        header.append(f'{date}_freq={freq_data[freq_idx]/1E9}GHz_lbd={299792458/freq_data[freq_idx]}m_xmin={A[0]}_xmax={B[0]}_y_min={A[1]}_ymax={B[1]}_stepx={pas_axe1}_stepy={pas_axe2}_average={count_avg}')
                    else:
                        header.append(f'{date}_freq={freq_data[freq_idx]/1E9}GHz_lbd={299792458/freq_data[freq_idx]}m_xmin={A[0]}_xmax={B[0]}_y_min={A[1]}_ymax={B[1]}_stepx={pas_axe1}_stepy={pas_axe2}')
                    header.append(f'note=[{note}]')
                    f.write("\t".join(header) + "\n")
                    for pos_idx in range(nb_tot_position):
                        line = [f"{x_val[pos_idx]:.3f}", f"{y_val[pos_idx]:.3f}"]
                        for trace_idx in range(len(trace_name)):
                            if pos_idx < len(all_mag[trace_idx]):
                                mag = all_mag[trace_idx][pos_idx]
                                phase = all_phase[trace_idx][pos_idx]
                                line.extend([f"{mag:.4f}", f"{phase:.4f}"])
                            else:
                                line.extend(["0.0000", "0.0000"])
                        f.write("\t".join(line) + "\n")
            print("Traitement terminé!")
            ################################################################################################
            # delete all "Balayage_i.txt" files
            ################################################################################################  
            motif = os.path.join(save_path, "Balayage_*.txt")
            fichiers = glob.glob(motif)
            for fichier in fichiers:
                os.remove(fichier)
            ################################################################################################
            # returning home, ask for error and closing connections
            ################################################################################################
            for axe in axis: 
                self.esp.write(f'{axe}PA0') # return to zero when the sweep is finished
                self.esp.write(f'{axe}WS')
            self.vna.close() 
            self.esp.close()
            print("Mesures terminées")
            print("Connexions fermées")
        except Exception as e:
            print(f"Erreur dans balayage_2D: {e}")
            try:
                for axe in axis:
                    self.esp.write(f'{axe}PA0') 
                    self.esp.write(f'{axe}WS')   
            except:
                pass
            try:
                self.vna.close()
                self.esp.close()
            except:
                pass
            raise  