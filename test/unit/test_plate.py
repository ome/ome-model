#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%
import pytest

from ome_model.experimental import Plate, Image, create_companion
import xml.etree.ElementTree as ElementTree

NS = {'OME': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'}
ElementTree.register_namespace('OME', NS['OME'])


class TestPlate(object):

    @pytest.mark.parametrize('rc', [True, False])
    def test_minimal_plate(self, tmpdir, rc):
        f = str(tmpdir.join('plate.companion.ome'))

        if rc:
            p = Plate("test", 1, 2)
        else:
            p = Plate("test")
        well = p.add_well(0, 0)
        i = Image("test", 256, 512, 3, 4, 5)
        well.add_wellsample(0, i)
        create_companion(plates=[p], out=f)

        root = ElementTree.parse(f).getroot()
        plates = root.findall('OME:Plate', namespaces=NS)
        assert len(plates) == 1
        assert plates[0].attrib['Name'] == 'test'
        if rc:
            assert plates[0].attrib['Rows'] == '1'
            assert plates[0].attrib['Columns'] == '2'
        wells = plates[0].findall('OME:Well', namespaces=NS)
        assert len(wells) == 1
        assert wells[0].attrib['Row'] == '0'
        assert wells[0].attrib['Column'] == '0'
        wellsamples = wells[0].findall('OME:WellSample', namespaces=NS)
        assert len(wellsamples) == 1
        imagerefs = wellsamples[0].findall('OME:ImageRef', namespaces=NS)
        assert len(imagerefs) == 1
        imageid = imagerefs[0].attrib['ID']
        images = root.findall('OME:Image', namespaces=NS)
        assert len(images) == 1
        assert images[0].attrib['Name'] == 'test'
        assert images[0].attrib['ID'] == imageid
        pixels = images[0].findall('OME:Pixels', namespaces=NS)
        assert len(pixels) == 1
        assert pixels[0].attrib['SizeX'] == '256'
        assert pixels[0].attrib['SizeY'] == '512'
        assert pixels[0].attrib['SizeZ'] == '3'
        assert pixels[0].attrib['SizeC'] == '4'
        assert pixels[0].attrib['SizeT'] == '5'
        assert pixels[0].attrib['DimensionOrder'] == 'XYZTC'
        assert pixels[0].attrib['Type'] == 'uint16'
        channels = pixels[0].findall('OME:Channel', namespaces=NS)
        assert len(channels) == 0

    def test_multiple_rows_columns_wellsamples(self, tmpdir):
        f = str(tmpdir.join('plate.companion.ome'))

        p = Plate("test", 4, 5)
        for row in range(4):
            for column in range(5):
                well = p.add_well(row, column)
                for field in range(6):
                    i = Image("test", 256, 512, 3, 4, 5)
                    well.add_wellsample(field, i)
        create_companion(plates=[p], out=f)

        root = ElementTree.parse(f).getroot()
        plates = root.findall('OME:Plate', namespaces=NS)
        assert len(plates) == 1
        assert plates[0].attrib['Name'] == 'test'
        wells = plates[0].findall('OME:Well', namespaces=NS)
        assert len(wells) == 20
        imageids = []
        for i in range(20):
            wellsamples = wells[i].findall('OME:WellSample', namespaces=NS)
            assert len(wellsamples) == 6
            for ws in wellsamples:
                imagerefs = ws.findall('OME:ImageRef', namespaces=NS)
                assert len(imagerefs) == 1
                imageids.append(imagerefs[0].attrib['ID'])
        assert len(imageids) == 120
        images = root.findall('OME:Image', namespaces=NS)
        assert len(images) == 120
        assert [x.attrib['ID'] for x in images] == imageids

    def test_multiple_plates_one_per_file(self, tmpdir):

        files = [str(tmpdir.join('%s.companion.ome' % i)) for i in range(4)]
        for i in range(4):
            p = Plate("test %s" % i, 1, 1)
            well = p.add_well(0, 0)
            img = Image("test %s" % i, 256, 512, 3, 4, 5)
            well.add_wellsample(0, img)
            create_companion(plates=[p], out=files[i])

        for i in range(4):
            root = ElementTree.parse(files[i]).getroot()
            plates = root.findall('OME:Plate', namespaces=NS)
            assert len(plates) == 1
            assert plates[0].attrib['Name'] == 'test %s' % i
            wells = plates[0].findall('OME:Well', namespaces=NS)
            assert len(wells) == 1
            wellsamples = wells[0].findall('OME:WellSample', namespaces=NS)
            assert len(wellsamples) == 1
            imagerefs = wellsamples[0].findall('OME:ImageRef', namespaces=NS)
            assert len(imagerefs) == 1
            images = root.findall('OME:Image', namespaces=NS)
            assert len(images) == 1
            assert images[0].attrib['Name'] == 'test %s' % i
