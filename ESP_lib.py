"""
Author : Louise Mousset
Date : 19/01/2026
"""

import pyvisa

class ESP_commande:
    def __init__(self, ip_adress_esp):
        """
        Establishes communication with the ESP motion controller using VISA addresses.
        Prints the identification string.

        Parameters
        ----------
        ip_adress_esp : string
            Ip adress of the ESP.

        Returns
        -------
        None.

        """
        try: 
            rm = pyvisa.ResourceManager()
            self.esp = rm.open_resource(f'{ip_adress_esp}')
            self.esp.timeout = 30000
            
            self.esp.write_termination = '\r' # I don't know why the motion controller needs this (but it does)
            self.esp.read_termination = '\r'
            print("Connecté à :", self.esp.query("*IDN?")) # ask identification
        except Exception as e:
            print(f"erreur lors de l'initialisation du moteur: {e}")
    
    def setup_axis_parameters(self, axis=2, units=2, speed=1, accel=5, deccel=5):
        """
        Docstring for setup_axis_parameters
        
        Parameters
        ----------
        axis : integer
            ESP axis number. The default is 2.
        units : integer
            The unit of the movement (0 = encoder count, 1 = motor step, 2 = millimeter,
            3 = micrometer, 4 = inches, 5 = milli-inches, 6 = micro-inches, 7 = degree, 8 = gradient,
            9 = radian, 10 = milliradian, 11 = microradian). The default is 2.
        speed : integer
            Speed mode of the axis (1 = slow, 2 = medium speed, 3 = fast). The default is 1.
        accel : integer or floating
            Acceleration of the movement (m.s−2). The default is 5.
        deccel : integer or floating
            Deceleration of the movement (m.s−2). The default is 5.
        """
        self.esp.write(f'{axis}MO')
        self.esp.write(f'{axis}SN{units}')
        self.esp.write(f'{axis}AC{accel}')
        self.esp.write(f'{axis}AG{deccel}')
        if speed==1:
            speed_mode = "JW5"
        elif speed==2:
            speed_mode = "JH10"
        elif speed==3:
            speed_mode = "VU15"
        self.esp.write(f'{axis}{speed_mode}')

    def move(self, axis=2, movement=1, absolute=True):
        """
        Moves a given axis with defined parameters.

        Parameters
        ----------
        axis : integer
            ESP axis number. The default is 2.
        movement : integer or floating
            The distance the given axis must move. The default is 1.
        absolute : boolean
            If True, the movement will be absolute; if False, it will be relative. The default is True.
        
        Returns
        -------
        None.

        """
        try: 
            # self.esp.write(f'{axis}MO')
            # self.esp.write(f'{axis}SN{units}')
            # self.esp.write(f'{axis}AC{accel}')
            # self.esp.write(f'{axis}AG{deccel}')
            # if speed==1:
            #     speed_mode = "JW5"
            # elif speed==2:
            #     speed_mode = "JH10"
            # elif speed==3:
            #     speed_mode = "VU15"
            # self.esp.write(f'{axis}{speed_mode}')
            
            print("Starting movement...")
            movement_mode = f'{"PA" if absolute else "PR"}'
            self.esp.write(f'{axis}{movement_mode}{movement}')
            self.esp.write(f'{axis}WS')
        except Exception as e:
            print(f"erreur lors du deplacement: {e}")
            
    def define_home(self, axis=2):
        """
        Defines the current position as the zero reference for the given axis.

        Parameters
        ----------
        axis : integer
            ESP axis number. The default is 2.

        Returns
        -------
        None.

        """
        try:
            self.esp.write(f'{axis}DH') # define the zero of the axis as the current position
        except Exception as e:
            print(f"erreur lors de la définition du zero: {e}")
        
    def return_home(self, axis=2):
        """
        Returns the axis to its defined home position.

        Parameters
        ----------
        axis : integer
            ESP axis number. The default is 2.

        Returns
        -------
        None.

        """
        try:
            self.esp.write(f'{axis}PA0') # return to the defined zero of the axis
            self.esp.write(f'{axis}WS') # wait for the the arm to stop moving
        except Exception as e:
            print(f"erreur lors du retour au zero: {e}")

    def give_unit_name(self, units):
        unit_name = {0:"encoder_count", 1:"motor_step", 2:"mm", 3:"µm", 4:"inches", 5:"milli-inches", 6:"micro-inches", 7:"deg", 8:"grad", 9:"rad", 10:"mili-rad", 11:"µ-rad"}[int(units)]
        return unit_name