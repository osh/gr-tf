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
import time, random
import numpy as np
import tensorflow as tf
from gnuradio import gr, blocks, audio
class interp(gr.sync_block):
    x = tf.placeholder("float32")

    def __init__(self, rate=0.333, dtype=np.complex64, sinc_width=10, sinc_size=1024):
        gr.sync_block.__init__(self,
            name="tf_interp",
            in_sig=[dtype],
            out_sig=[dtype])

        self.y = tf.placeholder(dtype)

        # set up history
        self.set_history(sinc_width*2)
        self.rate = rate
        self.offset = 0.0

        # Set up a sinc interpolation table 2D Vector [noffets,ntaps]
        self.sinc_size = sinc_size
        self.sinc_width = sinc_width
        sinc_offsets = np.arange(0,1.0,1.0/sinc_size)
        self.sinc_span = np.arange(-sinc_width,sinc_width)
        st_input = np.tile(sinc_offsets, [len(self.sinc_span),1]).T + self.sinc_span
        self.sinctable = np.sinc(st_input[::-1]).astype(dtype)

        # set up graph
        self.sess = tf.Session()
        self.op = self.tf_interp1d()

    def set_rate(self, rate):
        self.rate = rate

    def tf_interp1d(self):
        # Perform Sinc Interpolation
        iloc = tf.cast(self.x, tf.int32)
        frac = tf.cast( (self.x-tf.cast(iloc,tf.float32))*self.sinc_size, tf.int32 )
        inidx = tf.tile( tf.expand_dims(iloc,1), [1,self.sinctable.shape[1]]) + self.sinc_span
        inval = tf.gather(self.y,inidx+1)
        taps = tf.gather(self.sinctable, frac)
        out = tf.reduce_sum(inval*taps[:,:],1)
        return out

    def work(self, input_items, output_items):
        ival = input_items[0]
        sample_points = np.arange(self.offset+self.sinc_width, len(ival)-self.sinc_width, self.rate)
        if len(output_items[0] < len(sample_points)):
            sample_points = sample_points[0:len(output_items[0])]
        if len(sample_points > 0):
            self.offset = np.modf(sample_points[-1] + self.rate)[0]
            rv = self.sess.run([self.op], feed_dict={self.y:ival, self.x:sample_points})
            rvlen = len(rv[0])
            output_items[0][0:rvlen] = rv[0][:]
            return rvlen
        else:
            return 0

if __name__ == "__main__":
    blk = interp( rate=0.333, sinc_width=2, sinc_size=1024 )
    iv = [np.array([0,0,0,0,0,1,1,0,0,0], dtype=np.complex64)]
    ov = [np.array([0,0,0,0,0,1,1,0,0,0], dtype=np.complex64)]
    print "in",iv
    blk.work( iv,ov )
    print "out",ov

