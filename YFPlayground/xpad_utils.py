#!/usr/bin/env python3
# xpad_utils
# v1.0 6/28/23 YF - Created
#

# Special conversion - Sensor ADC Temperature
#double StParameter::convertSensorTemperature(uint32_t raw) const
#{
#    double val = convertSensorVoltage(raw);
#    return (3.2057 * val * val) - (53.749 * val) + 77.421;  // Per MM Keck PAD FPGA Information v0.2
#}


def convertSensorTemp(raw):
    dval = convertSensorVoltage(raw)
    return (3.2057 * dval * dval) - (53.749 * dval) + 77.421  #   // Per MM Keck PAD FPGA Information v0.2

#//---------------------------------------------
#// Special conversion - Sensor Raw ADC Voltage
#double StParameter::convertSensorVoltage(uint32_t raw) const
#{
#    double val = (raw >> 4) & 0xfff;   // limit to 12 bits
#    if (val >= 2048)
#    {
#        val = val - 4096;
#    }
#    return ( (val / 4096.0) + 0.5) * 3.01; // Per Sect 4.3.7.1, spec v1.4
#}

def convertSensorVoltage(raw):
    val = (raw >> 4) & 0xFFF
    if val >= 2048:
        val = val - 4096

    return ( (val / 4096.0) + 0.5) * 3.01 # ; // Per Sect 4.3.7.1, spec v1.4