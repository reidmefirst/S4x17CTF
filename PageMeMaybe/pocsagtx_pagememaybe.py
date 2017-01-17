#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Pocsagtx Hackrf
# Author: cstone@pobox.com
# Description: Example flowgraph for POCSAG transmitter
# Generated: Wed Dec 14 17:13:12 2016
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.filter import pfb
from optparse import OptionParser
import math
import mixalot
import osmosdr
import time
import fcntl
from subprocess import call

class pocsagtx_hackrf(gr.top_block):

    def __init__(self, inmessage, incapcode):
        gr.top_block.__init__(self, "Pocsagtx Hackrf")

        ##################################################
        # Variables
        ##################################################
        self.symrate = symrate = 38400
        self.samp_rate = samp_rate = 8000000
        self.pagerfreq = pagerfreq = 920612500
        self.max_deviation = max_deviation = 4500.0

        ##################################################
        # Blocks
        ##################################################
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
        	  float(samp_rate)/float(symrate),
                  taps=None,
        	  flt_size=16)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        	
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + "hackrf=0" )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(pagerfreq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(15, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna("", 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
          
        self.mixalot_pocencode_0 = mixalot.pocencode(1, 512, incapcode, inmessage, symrate)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((0.5, ))
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(2.0 * math.pi * max_deviation / float(symrate))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.mixalot_pocencode_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.analog_frequency_modulator_fc_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))



    def get_symrate(self):
        return self.symrate

    def set_symrate(self, symrate):
        self.symrate = symrate
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_pagerfreq(self):
        return self.pagerfreq

    def set_pagerfreq(self, pagerfreq):
        self.pagerfreq = pagerfreq
        self.osmosdr_sink_0.set_center_freq(self.pagerfreq, 0)

    def get_max_deviation(self):
        return self.max_deviation

    def set_max_deviation(self, max_deviation):
        self.max_deviation = max_deviation
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))

if __name__ == '__main__':
    lockfile = open("/home/krwightm/PageMe/lockfile.lck", 'w')
    fcntl.lockf(lockfile, fcntl.LOCK_EX) # block until the
    call(["/home/krwightm/PageMe/hackrfreset.sh"]) # this script should use usbreset to reset the hackrf
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-m", "--message", dest="message", help="message to send", metavar="MESSAGE", type="string")
    parser.add_option("-c", "--capcode", dest="capcode", help="pager capcode to send to", metavar="CAPCODE", type="int")
    (options, args) = parser.parse_args()
    message = options.message
    capcode = options.capcode
    print "Testing: message", message, "capcode", capcode
    tb = pocsagtx_hackrf(message, capcode)
    tb.start()
    time.sleep(5)
    tb.stop()
    tb.wait()
    fcntl.lockf(lockfile, fcntl.LOCK_UN) # free the lock!
