import os
import time
import numpy as np
from datetime import datetime
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy.optimize import curve_fit

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
        
def get_chi2(data, model, error):
    chi2 = np.sum((data - model)**2 / error**2)
    return chi2

def cos2(alpha, thetaE=0, amp=1):
    return amp *(np.cos(np.radians(thetaE - alpha)))**2

def cos4(alpha, thetaE=0, amp=1):
    return amp *(np.cos(np.radians(thetaE - alpha)))**4

def cos4_with_offset(alpha, thetaE=0, amp=1, offset=0):
    return amp *(np.cos(np.radians(thetaE - alpha)))**4 + offset

def cos2cos2(alpha, delta_theta, amp=1):
    return amp * np.cos(np.radians(alpha))**2 * (np.cos(np.radians(alpha + 90 - delta_theta))**2)

def cos2cos2_with_offset(alpha, delta_theta, amp=1, offset=0):
    return amp * np.cos(np.radians(alpha))**2 * (np.cos(np.radians(alpha + 90 - delta_theta))**2 + offset)


def common_colorbar(fig, cmap, vmin, vmax, label):
    """Créer une seule colorbar pour tous les plots"""

    cmap = plt.get_cmap(cmap)
    norm = Normalize(vmin=vmin, vmax=vmax)
   
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # nécessaire pour colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label(label)
    return cmap, norm, cbar


def plot_scat_coeff_angle(alpha, coeffs, traces, ifreqs, freq_samples, cmap='viridis', cbar_vmin=None, cbar_vmax=None, cbar_label='Fréquence [GHz]'):
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    ax = ax.flatten()
    
    cmap, norm, _ = common_colorbar(fig, cmap=cmap, vmin=cbar_vmin, vmax=cbar_vmax, label=cbar_label)

    for t in range(4):
        ax[t].set_title(traces[t])
        for f in ifreqs:
            color = cmap(norm(freq_samples[f]))
            ax[t].plot(alpha, coeffs[:, t, f], '.-', color=color)
        ax[t].set_xlabel("Alpha [°]")
        ax[t].set_ylabel(f"{traces[t]}")
        ax[t].grid(10)
    
    fig.tight_layout(rect=[0, 0, 0.9, 1])
    return fig, ax

def plot_scat_coeff_freq(freq_samples, coeffs, traces, ialpha, alpha, cmap='jet', cbar_vmin=None, cbar_vmax=None, cbar_label='Alpha [°]'):
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    ax = ax.flatten()
    
    cmap, norm, _ = common_colorbar(fig, cmap=cmap, vmin=cbar_vmin, vmax=cbar_vmax, label=cbar_label)

    for t in range(4):
        for a in ialpha:
            color = cmap(norm(alpha[a]))
            ax[t].plot(freq_samples, coeffs[a, t, :], '.-', color=color)
        ax[t].set_xlabel("Frequency [GHz]")
        ax[t].set_ylabel(f"{traces[t]}")
        ax[t].grid(10)

    
    fig.tight_layout(rect=[0, 0, 0.9, 1])
    return fig, ax

def myfit(x, y, model, p0=None, sigma=None, absolute_sigma=False, verbose=True):
    popt, pcov = curve_fit(model, x, y, p0=p0, sigma=sigma, absolute_sigma=absolute_sigma)
    error = np.sqrt(np.diag(pcov))

    # Residus et écart-type des résidus
    residuals = y - model(x, *popt)
    std_res = np.std(residuals)
    
    # chi2
    chi2 = get_chi2(y, model(x, *popt), std_res)
   
    # chi2 réduit to check goodness of fit
    chi2_red = chi2 / (len(x) - len(popt))

    if verbose:
        print("Paramètres optimisés :", popt)
        print("Erreurs sur les paramètres :", error)
        print("Écart-type des résidus :", std_res)
        print("Chi2 (calculé avec le STD sur les résidus du fit) :", chi2)
        print("Chi2 réduit :", chi2_red)

    return popt, error, residuals, chi2_red