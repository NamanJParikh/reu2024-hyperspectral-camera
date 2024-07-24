### Notes ###
# raw files should have the .raw file extension so they can be found by spectral
### Required Packages ###
# SpectralPython (spectral), tqdm, NumPy, SciPy, Matplotlib

### Imports ###
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from sklearn.linear_model import LinearRegression
import spectral.io.envi as envi
from spectral import imshow, view_cube
from tqdm import tqdm
from tqdm.contrib import itertools

### Constants ###
h = 6.626e-34 # Planck's constant
c = 299792458 # Speed of light
k = 1.380649e-23 # Boltzmann constant
b = 2.89777e-3 # Wien's constant

### Other Global Variables ###
image = None
units = None
wavelengths = None
spectrum = None
temp_arr = None

### Helper Functions ###

def blackbody(l, T, e, offset=0):
    """Blackbody radiation equation
    Input: l: wavelength, T: temperature, e: emissivity, 
            offset: used in fitting to account for stray light in the data
    Output: intensity of a blackbody at the given parameters"""
    return (e * ((2 * h * c**2) / l**5) * (1 / (np.exp((h * c) / (l * k * T)) - 1))) + offset

def construct_paths(folder_path):
    """ Constructs the paths to each of the relevant data files
    Input: path to hyperspectral data folder
    Output: list of paths to [raw hdr, raw raw, white reference hdr, white reference raw, 
                            dark reference hdr, dark reference raw, frame index file] """
    print("Constructing paths...")
    retval = []
    retval.append(folder_path + "/raw.hdr")
    retval.append(folder_path + "/raw")
    retval.append(folder_path + "/whiteReference.hdr")
    retval.append(folder_path + "/whiteReference")
    retval.append(folder_path + "/darkReference.hdr")
    retval.append(folder_path + "/darkReference")
    retval.append(folder_path + "/frameIndex.txt")
    return retval

def load_data(paths, quiet=False):
    """Input: paths list generated by (or in format of) construct_paths
    Output: hyperspectral tensor corrected by the white and dark references"""
    print("Loading data...")
    data_ref = envi.open(paths[0], paths[1])
    white_ref = envi.open(paths[2], paths[3])
    dark_ref = envi.open(paths[4], paths[5])

    white_tensor = np.array(white_ref.load())
    dark_tensor = np.array(dark_ref.load())
    data_tensor = np.array(data_ref.load())

    corrected_data = np.divide(
        np.subtract(data_tensor, dark_tensor),
        np.subtract(white_tensor, dark_tensor))

    if not quiet:
        print(corrected_data)
    return corrected_data

def get_bands(paths, quiet=False):
    """Input: paths list generated by (or in format of) construct_paths
    Output: (Array of wavelength bands, wavelength units string)"""
    print("Getting wavelength bands...")
    global wavelengths
    global units
    file = open(paths[0], 'r')
    text = file.read()

    start_id = "\nwavelength = {\n"
    start_index = text.find(start_id) + len(start_id)
    end_id = "\n}\n;AOI height"
    end_index = text.find(end_id)
    wavelengths = text[start_index:end_index]
    wavelengths = np.array(wavelengths.split("\n,"), dtype=np.float32)

    units_id = "wavelength units = "
    units_index = text.find(units_id) + len(units_id)
    units = text[units_index:text.find(start_id)]

    if not quiet:
        print(f"Units = {units}")
        print(f"Number wavelengths = {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")

    return None

def compress_horiz_slice(data, start_idx, end_idx):
    return np.array([np.divide(np.sum(data[:,start_idx:end_idx,:],axis=1), 
                     end_idx-start_idx)])

def shrink_image(chunk_size=10, quiet=False):
    global image

    for itera in range(2):
        horiz_slices = []
        for i in range(image.shape[1] // chunk_size):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size
            if end_idx < image.shape[1]:
                horiz_slices.append(compress_horiz_slice(image, start_idx, end_idx))
            elif start_idx == image.shape[1]:
                continue
            else:
                horiz_slices.append(compress_horiz_slice(image, start_idx, image.shape[1]))

        image = np.concatenate(tuple(horiz_slices), axis=0)

    return image

def fit_spectrum(quiet=False, check_units=True):
    """Fits the selected spectrum
    Input: None (uses global variables)
    Output: Fitted parameters, final least squares cost"""
    if check_units:
        print("\nIf this test fails, check lower in this function to adjust wavelenght unit conversion to m")
        print("Checking that units are nm... ", end="")
        assert(units == "nm")
        print("Passed")
    if not quiet:
        print("Fitting spectrum...")

    # params = [a0, a1, a2, offset, T]
    params0 = np.array([1, 1, 1, 0.1, 1000])
    def intensity(params, l):
        e = params[0] + (params[1] * l) + (params[2] * l**2)
        return blackbody(l, params[4], e, params[3])
    
    def residuals(params):
        result = []
        for i in range(len(wavelengths)):
            Si = intensity(params, wavelengths[i] * 1e-9) # assuming units are nm
            St = spectrum[i]
            result.append(Si - St)
        return np.array(result)

    result = least_squares(residuals, params0)

    if not quiet:
        yfit = []
        for l in wavelengths:
            yfit.append(intensity(result.x, l * 1e-9))

        plt.figure(figsize=(5,5))
        plt.scatter(wavelengths, spectrum, s=5)
        plt.scatter(wavelengths, yfit, s=5)
        plt.title(f"Fitted Spectrum for Position ({pixel[0]}, {pixel[1]})", fontsize=15)
        plt.xlabel(f"Wavelength [{units}]", fontsize=12)
        plt.xticks(fontsize=10)
        plt.ylabel("Intensity [arb. units]", fontsize=12)
        plt.yticks([])
        plt.legend(["Actual", "Fitted"], fontsize=10)
        plt.show()

    return result.x, result.cost

### Analysis ###

def analysis(folder_path):
    global image
    global pixel
    global spectrum
    global temp_arr

    paths = construct_paths(folder_path)
    image = load_data(paths, quiet=True)
    _ = get_bands(paths, quiet=True)

    _ = shrink_image()

    temp_arr = np.zeros((image.shape[0], image.shape[1]))
    for (i,j) in itertools.product(range(image.shape[0]), range(image.shape[1])):
        spectrum = image[i][j]
        try:
            result, cost = fit_spectrum(quiet=True, check_units=False)
            temp_arr[i][j] = result[-1]
        except: temp_arr[i][j] = -1
    
    return temp_arr

if __name__ == "__main__": print("This file should not be run directly...")