#!/usr/bin/env python
#
# Copyright 2016 Tim O'Shea
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import numpy, time, random
import tensorflow
from gnuradio import gr, blocks, audio
class fir(gr.sync_block):
    # some consts
    x = tensorflow.placeholder("complex64")
    y = tensorflow.placeholder("complex64")

    def set_taps(self, taps):
        print "set_taps"
        taps = numpy.array(taps)
        self.b = tensorflow.Variable(numpy.vstack([taps]))
        self.set_history(taps.size)

    def __init__(self, taps):
        gr.sync_block.__init__(self,
            name="tf_fir",
            in_sig=[numpy.float32],
            out_sig=[numpy.float32])
        self.set_taps(taps)
        self.sess = tensorflow.Session()
        self.op = tensorflow.reduce_sum( self.x, keep_dims=True)


    def work(self, input_items, output_items):
        ival = input_items[0]
        rv = self.sess.run([self.op], feed_dict={self.x:ival})
        output_items[0][:] = numpy.array(rv, dtype=numpy.complex64)
        return len(output_items[0])

if __name__ == "__main__":
    blk = fir( [1,2,3,4] )
    iv = [numpy.array([0,0,0,0,0,1,1,0,0,0], dtype=numpy.complex64)]
    ov = [numpy.array([0,0,0,0,0,1,1,0,0,0], dtype=numpy.complex64)]
    print "in",iv
    blk.work( iv,ov )
    print "out",ov

