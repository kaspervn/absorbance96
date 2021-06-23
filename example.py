import serial
import serial.tools.list_ports

from absorbance96 import Absorbance96
from utils import *


def find_unique_dev_by_pidvid(pid: int, vid: int):
    found_devices = list(filter(lambda p: p.pid == pid and p.vid == vid, serial.tools.list_ports.comports()))
    return found_devices[0] if len(found_devices) == 1 else None

def connect_absorbance():
    ser_dev = find_unique_dev_by_pidvid(24597, 1027)
    if ser_dev != None:
        return Absorbance96(serial.Serial(ser_dev.device, baudrate=115200))
    else:
        return None

absorbance_meter = connect_absorbance()
if absorbance_meter:
    print('Connected to absorbance96 meter')
else:
    print('Could not find exactly one absorbance96 meter')
    exit(1)

available_filters = absorbance_meter.get_filters()
print(f'available wavelengths: {",".join(map(str, available_filters.values()))}')

filter_600_index = check_and_assert_wavelength_index(available_filters, 600)

do_interactive_calibration(absorbance_meter, filter_600_index)
results, results_raw = absorbance_meter.read_plate(filter_600_index)
error = check_absorbance_error_and_report(absorbance_meter, do_exit=True)
pretty_print_measurement_data(results)
