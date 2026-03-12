import ESP_lib as espl

#motor_controller_ip_xy = "GPIB0::1::INSTR" # Scan XY
motor_controller_ip_ang = "GPIB0::2::INSTR" # Angular scan 

espc = espl.ESP_commande(motor_controller_ip_ang)

# Single mouvement
#units = 7 # Deg
#espc.setup_axis_parameters(axis=1, units=units, speed=1, accel=5, deccel=5)
#espc.move(axis=1, movement=-0.1, absolute=False)


# Define Home => Move => Return to home => Move again
#espc.define_home(axis=1)
# espc.move(axis=1, movement=5, absolute=False)
espc.return_home(axis=1)
# espc.move(axis=1, movement=10, absolute=False)

