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
import numpy as np
import tensorflow
from gnuradio import gr, blocks, audio
class autocorr(gr.sync_block):
    # some consts
    x = tensorflow.placeholder("complex64")

    def __init__(self, aclen=1000, nfft=4092, shift=1024, avg=True):
        gr.sync_block.__init__(self,
            name="tf_autocorr",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32])

        self.aclen = aclen
        self.nfft = nfft
        self.shift = shift
        self.sess = tensorflow.Session()
        self.avg = avg
        self.alpha = 1e-5       # IIR update rate
        self.n_aggregate = 100  # force large work functions
    
        # set up variables ...
        self.u = tensorflow.Variable(np.zeros([self.aclen], dtype='float32'))
        self.sess.run([tensorflow.initialize_all_variables()])
        self.o1 = self.op()
        self.set_output_multiple(self.n_aggregate*aclen)

    def work(self, input_items, output_items):
        ival = input_items[0]
        blks = int(np.ceil((len(ival)-(self.nfft))*1.0/self.shift))
        iv = np.zeros([blks, self.nfft], dtype='complex64')
        for i in range(blks):
            iv[i,:] = ival[i*self.shift:i*self.shift+self.nfft]
        rv = self.sess.run([self.o1], feed_dict={self.x:iv})
        if self.avg:
            nout = self.aclen
            output_items[0][0:nout] = np.reshape(rv, [nout])
            return nout
        else:
            nout = self.aclen*blks
            output_items[0][0:nout] = np.reshape(rv, [nout])
            return nout

    def op(self):
        xf = tensorflow.fft(self.x)
        x2 = xf * tensorflow.conj(xf)
        xt = tensorflow.ifft(x2)
        xr = 10*tensorflow.log( tensorflow.abs( xt[:,0:self.aclen] ) )
 
        if self.avg:
            N = tensorflow.shape(xr)[0]
            idx = tensorflow.cast(tensorflow.range(0,N), tensorflow.float32)
            s = tensorflow.reshape( self.alpha * tensorflow.pow( (1-self.alpha), idx ), [N,1] )
            self.u = tensorflow.pow( (1-self.alpha), tensorflow.cast(N,tensorflow.float32) )*self.u  +  tensorflow.reduce_sum(s*xr, 0)
            return self.u
        else:
            return xr

if __name__ == "__main__":
    blk = autocorr(1000, 2048, 1024)
    nsamp = 10000
    iv = (numpy.random.randn(nsamp) + 1j*numpy.random.randn(nsamp)).astype("complex64")
    ov = numpy.zeros([nsamp])
    print "in",iv
    blk.work( [iv],[ov] )
    blk.work( [iv],[ov] )
    print "out",ov



