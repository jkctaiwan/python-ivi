"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2016-2017 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .tektronixMDO4000 import *
from .tektronixMDOAFG import *
import re


class tektronixMDO4104C(tektronixMDO4000, tektronixMDOAFG):
    "Tektronix MDO4104C IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault("_instrument_id", "MDO4104C")

        super().__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 16
        self._bandwidth = 1e9

        # AFG option
        self._output_count = 1

        # Add fetch isf
        self._add_method(
            "channels[].measurement.fetch_isf",
            self._measurement_fetch_isf,
            ivi.Doc(
                """
                        This function calls self._ask_raw(b':WAVFrm?') and format the raw bytearray as
                        ISF file format, and return the raw byte again.
                        """
            ),
        )

        self._init_channels()
        self._init_outputs()


    def _measurement_fetch_isf(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return b""

        self._write(":data:source %s" % self._channel_name[index])
        self._write(":data:encdg fastest")
        self._write(":data:width 2")
        self._write(":data:start 1")
        self._write(":data:stop 1e10")
        # eanble verbosity
        self._write(":HEADer ON")
        # check if the channel is valid
        if 'NR_PT' not in self._ask(':WFMOutpre?'):
            raise Exception(f"Channel {self._channel_name[index]} has no waveform data")
        # Read whole thing
        isf_unformatted = b""
        try:
            isf_unformatted = self._ask_raw(b":WAVFrm?")
        except Exception as e:
            print(e)
        finally:
            # reset the verbosity
            self._write(":HEADer OFF")

        return isf_unformatted


    def __del__(self):
        self.close()

