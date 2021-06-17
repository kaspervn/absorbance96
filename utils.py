import sys

import numpy as np
from more_itertools import first_true
from tabulate import tabulate

from absorbance96 import Absorbance96


def pretty_print_measurement_data(data, file=sys.stdout):
    restructred_data = np.array(data).reshape((12, 8)).astype(str).transpose()
    restructred_data = np.concatenate((np.array([['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']]).transpose(), restructred_data), axis=1)
    print(tabulate(restructred_data, headers=tuple(map(str, range(0,13)))), file=file)


def check_absorbance_error_and_report(absorbance_dev: Absorbance96, do_exit=False):
    err_code = absorbance_dev.get_error()
    if err_code != 0:
        print(f'Device reported error: {Absorbance96.get_error_msg(err_code)}')
        if do_exit:
            exit(1)
        else:
            return err_code
    else:
        return err_code


def do_interactive_calibration(absorbance_dev: Absorbance96, main_wavelength: int):
    print("Let's do a calibration!")
    print("Please remove the plate from the absorbance meter, and then press enter")
    input()
    print('Doing calibration...')
    result = absorbance_dev.calibrate(main_wavelength)
    print(f'Done. result: {result}')
    check_absorbance_error_and_report(absorbance_dev, do_exit=True)
    print('Now place back the plate and then press enter')
    input()

def check_and_assert_wavelength_index(available_filters, given_wavelength):
    search_filter = lambda wavelength: first_true(available_filters.keys(), None,
                                                  lambda x: int(available_filters[x]) == wavelength)
    wavelength_id = search_filter(given_wavelength)

    if wavelength_id is None:
        print(f'Wavelength {given_wavelength} not supported by machine. Choose from {", ".join(map(str, available_filters.values()))}')
        exit(1)

    return wavelength_id