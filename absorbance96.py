import serial
from more_itertools import flatten

ERROR_CODES = {
    0: 'OK',
    1: 'OPTICAL PROBLEM',
    2: 'AMBIENT LIGHT EXCEEDED',
    3: 'USB POWER INSUFFICIENT',
    4: 'HARDWARE ERROR',
    5: 'TEMPERATURE'
}

class Absorbance96:

    def __init__(self, port: serial.Serial):
        self.port = port
        self.port.timeout = 10

    def _do_command(self, cmd, postample):
        self.port.write(f'{cmd}\r'.encode())

        self.port.read_until(f'{cmd}\r'.encode())

        return list(filter(lambda x: x != '', [x.decode().strip() for x in self.port.read_until(f'{postample}'.encode()).split(b'\n')][:-1]))

    # For debugging
    def _do_command_raw(self, cmd, postample):
        self.port.write(f'{cmd}\r'.encode())

        self.port.read_until(f'{cmd}\r'.encode())

        return self.port.read_until(f'{postample}'.encode())

    # Returns a dict with all the available. Maps filter-index to wavelength
    def get_filters(self):
        return dict(tuple(map(int, x.split('='))) for x in self._do_command('!GETFILT()', '#GETFILT()')[0].split(','))

    # Returns True if a microplate is in the device or state is not known. False otherwise
    def get_plate(self):
        return bool(int(self._do_command('!PLATE()', '#PLATE()')[0]))

    # Performs calibration for measuring with filter `x` and reference filter `y`. `x` and `y` are filter indices.
    # If no reference is to be used, use it's default value of -1
    def calibrate(self, x: int, y: int = -1):
        return ', '.join(self._do_command(f'!CALIBRATE({x},{y})', '#CALIBRATE()'))

    # Performs a measurement with filter `x` and reference filter `y`. `x` and `y` are filter indices.
    # If no reference is to be used, use it's default value of -1
    # Returns the values in the following order: A1 to H1, A2 to H2...
    def read_plate(self, x: int, y: int = -1):
        result_lines = self._do_command(f'!RPF({x},{y})', '#RP()')

        well_values = list(flatten((float(x) for x in y.split(' ')) for y in result_lines[:12]))

        return well_values, result_lines[12:]

    # Gets the error state as an error number. `0` means no error. Use `get_error_msg` to determine what's wrong
    def get_error(self):
        return int(self._do_command('!ERROR()', '#ERROR()')[0])

    @staticmethod
    def get_error_msg(code):
        return ERROR_CODES[code]