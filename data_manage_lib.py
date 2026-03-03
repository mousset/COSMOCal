import os
import time
import numpy as np
from datetime import datetime
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# test

def save_measurement_to_fits(freqs, mag, phi, save_path, filename="measurement.fits", header_info=None):
    """
    Save magnitude and phase data to a FITS file with header information.
    
    Parameters
    ----------
    freqs : np.array
        Frequency samples.
    mag : np.ndarray
        Magnitude array with shape (nsteps, nS_parameters, nfreq_points)
    phi : np.ndarray
        Phase array with same shape as mag
    save_path : str
        Directory path where the FITS file will be saved
    filename : str
        Name of the FITS file (default: "measurement.fits")
    header_info : dict, optional
        Dictionary containing header metadata (e.g., freq range, trace names, scan parameters)
        
    Returns
    -------
    None
    """
    os.makedirs(save_path, exist_ok=True)
    full_path = os.path.join(save_path, filename)
    
    # Create primary HDU with frequency samples
    hdu_freqs = fits.PrimaryHDU(data=freqs)
    hdu_freqs.header['DATATYPE'] = 'Frequency samples in GHz'
    
    # Create secondary HDU with magnitude data
    hdu_mag = fits.ImageHDU(data=mag, name='MAGNITUDE')
    hdu_mag.header['DATATYPE'] = 'Magnitude in dB'

    # Create third HDU with phase data
    hdu_phi = fits.ImageHDU(data=phi, name='PHASE')
    hdu_phi.header['DATATYPE'] = 'Phase in degrees'
    
    # Add header information if provided
    if header_info:
        for key, value in header_info.items():
            # Limit key length to 8 characters as per FITS standard
            fits_key = key[:8] if len(key) > 8 else key
            if isinstance(value, str):
                hdu_freqs.header[fits_key] = value
            elif isinstance(value, (int, float)):
                hdu_freqs.header[fits_key] = value
    
    # Create HDU list and write to file
    hdul = fits.HDUList([hdu_freqs, hdu_mag, hdu_phi])
    hdul.writeto(full_path, overwrite=True)
    print(f"FITS file saved: {full_path}")

def get_colors(n_steps, cmap_name='Blues', vmin=0, vmax=None):
    if vmax is None:
        vmax = n_steps - 1
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap_name)
    return [cmap(norm(i)) for i in range(n_steps)], norm, cmap

def has_key(hdul, key='THETA_R'):
    """Retourne True si THETA_R existe dans le header"""
    return key in hdul[0].header

def rename_header_key(fits_file, old_key, new_key, save=True):
    """Renomme une clé dans le header FITS"""
    with fits.open(fits_file, mode='update') as hdul:
        if old_key in hdul[0].header:
            value = hdul[0].header[old_key]
            hdul[0].header[new_key] = value
            del hdul[0].header[old_key]
            if save:
                hdul.flush()
            print(f"✓ Clé '{old_key}' renommée en '{new_key}' avec valeur: {value}")
            return True
        else:
            print(f"✗ Clé '{old_key}' non trouvée dans le header")
            return False