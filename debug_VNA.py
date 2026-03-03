import time
import VNA_lib as vnal
import pyvisa
import matplotlib.pyplot as plt
import numpy as np

# This script is used to debug the VNA communication and configuration.
# See https://helpfiles.keysight.com/csg/e5080b/index.htm#t=Home.htm&rhsearch=python to find the commands

### Standard Commands for Programmable Instruments (SCPI) are used to control the VNA.
### SCPI is not case sensitive

### OPEN COMMUNICATION WITH THE VNA
vna_ip = "GPIB0::16::INSTR"  # adresse IP du VNA
rm = pyvisa.ResourceManager()
session = rm.open_resource(f'{vna_ip}')
session.timeout = 30000  # timeout of 30 sec
print("Connecté à :", session.query("*IDN?")) # ask identification


#### CREATE A FIGURE OF MERITE (FOM) MEASUREMENT
# Command to preset the instrument and deletes the default trace, measurement, and window
# vna.write("SYST:FPR")

# # Create and turn on window 1
# vna.write("DISP:WIND1:STAT ON")

# # Create a measurement with parameter
# vna.write("CALC1:MEAS1:DEF 'S21'")

# # Displays measurement 1 in window 1 and assigns the next available trace number to the measurement
# vna.write("DISP:MEAS1:FEED 1")

# # Set the start and stop frequencies
# vna.write("SENS1:FREQ:START 1e9")
# vna.write("SENS1:FREQ:STOP 2e9")

# # Set the receivers to be 2e9 -> 3e9
# # See SENS:FOM:RNUM? to find the range number for a specific name
# vna.write("SENS1:FOM:RANG3:FREQ:OFFS 1e9")

# # Turns frequency offset on and enable the freq offset settings

# vna.write("SENS1:FOM ON")




Cal_file = "wr6-5_25022026.csa"
session.write(':MMEM:LOAD:FILE "%s"' % (f'D:/{Cal_file}'))
###### CREATE A S-Parameter MEASUREMENT
# Command to preset the instrument and deletes the default trace, measurement, and window
# session.write("SYST:FPR")


# # Create and turn on window 1
# session.write("DISP:WIND1:STAT ON")

# # Create a S21 measurement
# session.write("CALC1:MEAS1:DEF 'S21'")

# # Displays measurement 1 in window 1 and assigns the next available trace number to the measurement
# session.write("DISP:MEAS1:FEED 1")

# # Set the active measurement to measurement 1
# session.write("CALC1:PAR:MNUM 1")

# # Set sweep type to linear
# session.write("SENS1:SWE:TYPE LIN")

# # Perfoms a single sweep
# session.write("SENS1:SWE:MODE SING")
# opcCode = session.query("*OPC?")

# # Get stimulus and formatted response data

# session.write(f'CALC1:FORM PHAS')
# results = session.query_ascii_values(f'CALC1:DATA? FDATA')
# #query_ascii_values("CALC1:MEAS1:DATA:FDATA?")
# xValues = session.query_ascii_values("CALC1:MEAS1:X:VAL?")

# print(len(xValues), len(results))
# plt.plot(xValues, results)
# plt.ylabel("dB")
# plt.xlabel("Frequency")
# plt.show()





# # Create and turn on window 1
#session.write("DISP:WIND1:STAT ON")


def setup_traces(Sparameters = ["S21", "S12", "S11", "S22"]):
    nS = len(Sparameters)
    trace_num = np.arange(1, nS+1)
    print(trace_num)

    ### delete all the default measurements
    session.write("CALC1:MEAS:DEL:ALL") 
    
    for i in range(nS):
        trace_name = Sparameters[i]
        # Create a measurement for the S parameter
        session.write(f"CALC1:MEAS{i+1}:DEF '{trace_name}'")

        # Displays each measurement in a different window
        # It assigns the next available trace number to the measurement
        session.write(f"DISP:WIND{i+1}:TRAC1:FEED '{trace_name}'")
        #session.write(f"DISP:MEAS{i+1}:FEED {i+1}")

    time.sleep(3) # Give it some time 
    # Autoscale all traces in each window
    for i in range(nS): 
        session.write(f"DISP:WIND{i+1}:Y:AUTO")

    trace = Sparameters[0]
    session.write(f'CALC1:PAR:SEL {trace}')

    return

setup_traces()

# # # ======================== Set up 4 S-Parameters ========================
# # # Create a S11 measurement
# #session.write("CALC:MEAS2:DEL")
# session.write("CALC:MEAS:DEL:ALL") # delete all the default measurements


# session.write("CALC1:MEAS1:DEF 'S11'")

# # # Displays measurement 1 in window 1 and assigns the next available trace number to the measurement
# session.write("DISP:MEAS1:FEED 1") # feed the measurement to trace 1 and autoscale the trace

# #session.write(f':DISP:WIND{window}:TRAC{trace_number}:Y:AUTO') # autoscale the trace


# # Create a S21 measurement
# session.write("CALC1:MEAS2:DEF 'S21'")

# # Displays measurement 2 in window 2 and assigns the next available trace number to the measurement
# session.write("DISP:MEAS2:FEED 2")


# # Create a S12 measurement
# session.write("CALC1:MEAS3:DEF 'S12'")
# # Displays measurement 3 in window 1 and assigns the next available trace number to the measurement
# session.write("DISP:MEAS3:FEED 3")

# #session.write("DISP:MEAS3:Y:AUTO")

# # Create a S22 measurement
# session.write("CALC1:MEAS4:DEF 'S22'")
# # Displays measurement 4 in window 1 and assigns the next available trace number to the measurement
# session.write("DISP:MEAS4:FEED 4")


# time.sleep(4)   
# session.write("DISP:WIND1:Y:AUTO")
# session.write("DISP:WIND2:Y:AUTO")
# session.write("DISP:WIND3:Y:AUTO")
# session.write("DISP:WIND4:Y:AUTO")


# # ======================== Set start and stop ========================
# session.write("SENS1:FREQ:START 1e9")

# session.write("SENS1:FREQ:STOP 2e9")

# # ======================== Change the number of points ========================
# session.write("SENS1:SWE:POIN 51")

# # ======================== Set IFBW ========================
# # Set IF Bandwidth to 700 Hz
# session.write("SENS1:BAND 700")

# # ======================== Take a sweep and read back data ========================
# # Perfoms a single sweep
# session.write("SENS1:SWE:MODE SING")
# opcCode = session.query("*OPC?")
# results1 = session.query_ascii_values("CALC1:MEAS1:DATA:FDATA?")
# results2 = session.query_ascii_values("CALC1:MEAS2:DATA:FDATA?")
# results3 = session.query_ascii_values("CALC1:MEAS3:DATA:FDATA?")
# results4 = session.query_ascii_values("CALC1:MEAS4:DATA:FDATA?")



