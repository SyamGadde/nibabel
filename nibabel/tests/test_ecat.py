# emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the NiBabel package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
import os
from StringIO import StringIO
import numpy as np

from ..testing import assert_equal, assert_not_equal, \
    assert_true, assert_false, assert_raises

from numpy.testing import (assert_array_equal,
                           assert_array_almost_equal)


from ..ecat import EcatHeader, EcatMlist, EcatSubHeader, EcatImage
import test_binary as tb
from ..testing import parametric, data_path, ParametricTestCase

ecat_file = os.path.join(data_path, 'tinypet.v')

class TestEcatHeader(ParametricTestCase):
    header_class = EcatHeader
    example_file = ecat_file

    def test_header_size(self):
        yield assert_equal(self.header_class._dtype.itemsize, 502)

    def test_empty(self):
        hdr = self.header_class()
        yield assert_true(len(hdr.binaryblock) == 502)
        yield assert_true(hdr['magic_number'] == 'MATRIX72')
        yield assert_true(hdr['sw_version'] == 74)
        yield assert_true(hdr['num_frames'] == 0)
        yield assert_true(hdr['file_type'] == 0)
        yield assert_true(hdr['ecat_calibration_factor'] == 1.0)

    def test_dtype(self):
        hdr = self.header_class()
        yield assert_raises(NotImplementedError,
                            hdr.get_data_dtype)

    def test_copy(self):
        hdr = self.header_class()
        hdr2 = hdr.copy()
        yield assert_true(hdr == hdr2)
        yield assert_true(not hdr.binaryblock == hdr2._header_data.byteswap().tostring())
        yield assert_true(hdr.keys() == hdr2.keys())

    def test_update(self):
        hdr = self.header_class()
        yield assert_true(hdr['num_frames'] == 0)
        hdr['num_frames'] = 2
        yield assert_true(hdr['num_frames'] == 2)
    
    def test_endianness(self):
        fid = open(ecat_file)
        hdr = self.header_class()
        newhdr = hdr.from_fileobj(fid)
        fid.close()
        yield assert_true(hdr.endianness == '<')
        yield assert_true(newhdr.endianness == '>')
