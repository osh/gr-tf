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
class add(gr.sync_block):
    x = tensorflow.placeholder("complex64")
    y = tensorflow.placeholder("complex64")

    def __init__(self, taps):
        gr.sync_block.__init__(self,
            name="tf_add",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.sess = tensorflow.Session()
        self.op = tensorflow.add( self.x, self.y)

    def work(self, input_items, output_items):
        rv = self.sess.run([self.op], feed_dict={self.x:input_items[0], self.y:input_items[1]})
        output_items[0][:] = rv[0]
        return len(rv[0])

if __name__ == "__main__":
    blk = add( [1,2,3,4] )
    iv1 = [numpy.array([0,0,0,0,1,1,1,0,0,0], dtype=numpy.complex64)]
    iv2 = [numpy.array([0,0,0,0,0,0,1,8,0,0], dtype=numpy.complex64)]
    iv = [iv1, iv2]
    ov = [numpy.array([0,0,0,0,0,0,0,0,0,0], dtype=numpy.complex64)]
    print "in",iv
    blk.work( iv,ov )
    print "out",ov

