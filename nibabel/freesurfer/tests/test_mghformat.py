# emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the NiBabel package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
'''Tests for mghformat reading writing'''
from __future__ import with_statement
import os
import numpy as np
from .. import load, save, MGHImage
from ..mghformat import MGHError
from ...tmpdirs import InTemporaryDirectory
from ...testing import data_path
from numpy.testing import assert_equal, assert_array_equal, \
    assert_array_almost_equal, assert_almost_equal, assert_raises

# sample voxel to ras matrix
v2r = np.array([[1, 2, 3, -13], [2, 3, 1, -11.5],
                [3, 1, 2, -11.5], [0, 0, 0, 1]], dtype=np.float32)


def test_read_mgh():
    # test.mgz was generated by the following command
    # mri_volsynth --dim 3 4 5 2 --vol test.mgz
    # --cdircos 1 2 3 --rdircos 2 3 1 --sdircos 3 1 2
    # mri_volsynth is a FreeSurfer command
    mgz_path = os.path.join(data_path, 'test.mgz')
    mgz = load(mgz_path)

    # header
    h = mgz.get_header()
    assert_equal(h['version'], 1)
    assert_equal(h['type'], 3)
    assert_equal(h['dof'], 0)
    assert_equal(h['goodRASFlag'], 1)
    assert_array_equal(h['dims'], [3, 4, 5, 2])
    assert_array_almost_equal(h['mrparms'], [2.0, 0.0, 0.0, 0.0])
    assert_array_almost_equal(h.get_vox2ras(), v2r)

    # data. will be different for your own mri_volsynth invocation
    v = mgz.get_data()
    assert_almost_equal(v[1, 2, 3, 0], -0.3047, 4)
    assert_almost_equal(v[1, 2, 3, 1], 0.0018, 4)


def test_write_mgh():
    # write our data to a tmp file
    v = np.arange(120)
    v = v.reshape((5, 4, 3, 2)).astype(np.float32)
    # form a MGHImage object using data and vox2ras matrix
    img = MGHImage(v, v2r)
    with InTemporaryDirectory():
        save(img, 'tmpsave.mgz')
        # read from the tmp file and see if it checks out
        mgz = load('tmpsave.mgz')
        h = mgz.get_header()
        dat = mgz.get_data()
        # Delete loaded image to allow file deletion by windows
        del mgz
    # header
    assert_equal(h['version'], 1)
    assert_equal(h['type'], 3)
    assert_equal(h['dof'], 0)
    assert_equal(h['goodRASFlag'], 1)
    assert_array_equal(h['dims'], [5, 4, 3, 2])
    assert_array_almost_equal(h['mrparms'], [0.0, 0.0, 0.0, 0.0])
    assert_array_almost_equal(h.get_vox2ras(), v2r)
    # data
    assert_almost_equal(dat, v, 7)


def test_write_noaffine_mgh():
    # now just save the image without the vox2ras transform
    # and see if it uses the default values to save
    v = np.ones((7, 13, 3, 22)).astype(np.uint8)
    # form a MGHImage object using data
    # and the default affine matrix (Note the "None")
    img = MGHImage(v, None)
    with InTemporaryDirectory():
        save(img, 'tmpsave.mgz')
        # read from the tmp file and see if it checks out
        mgz = load('tmpsave.mgz')
        h = mgz.get_header()
        # Delete loaded image to allow file deletion by windows
        del mgz
    # header
    assert_equal(h['version'], 1)
    assert_equal(h['type'], 0)  # uint8 for mgh
    assert_equal(h['dof'], 0)
    assert_equal(h['goodRASFlag'], 1)
    assert_array_equal(h['dims'], [7, 13, 3, 22])
    assert_array_almost_equal(h['mrparms'], [0.0, 0.0, 0.0, 0.0])
    # important part -- whether default affine info is stored
    ex_mdc = np.array([[-1, 0, 0],
                       [0, 0, -1],
                       [0, 1, 0]], dtype=np.float32)
    assert_array_almost_equal(h['Mdc'], ex_mdc)

    ex_pxyzc = np.array([0, 0, 0], dtype=np.float32)
    assert_array_almost_equal(h['Pxyz_c'], ex_pxyzc)


def bad_dtype_mgh():
    ''' This function raises an MGHError exception because
    uint16 is not a valid MGH datatype.
    '''
    # try to write an unsigned short and make sure it
    # raises MGHError
    v = np.ones((7, 13, 3, 22)).astype(np.uint16)
    # form a MGHImage object using data
    # and the default affine matrix (Note the "None")
    img = MGHImage(v, None)
    with TemporaryDirectory() as tmpdir:
        save(img, os.path.join(tmpdir, 'tmpsave.mgz'))
        # read from the tmp file and see if it checks out
        mgz = load(os.path.join(tmpdir, 'tmpsave.mgz'))


def test_bad_dtype_mgh():
    # Now test the above function
    assert_raises(MGHError, bad_dtype_mgh)
