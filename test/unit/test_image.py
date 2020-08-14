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


from ome_model.experimental import Image, create_companion
import pytest
import xml.etree.ElementTree as ElementTree

NS = {'OME': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'}
ElementTree.register_namespace('OME', NS['OME'])


class TestImage(object):

    def test_minimal_image(self, tmpdir):
        f = str(tmpdir.join('image.companion.ome'))

        i = Image("test", 256, 512, 3, 4, 5)
        create_companion(images=[i], out=f)

        root = ElementTree.parse(f).getroot()
        images = root.findall('OME:Image', namespaces=NS)
        assert len(images) == 1
        assert images[0].attrib['Name'] == 'test'
        pixels = images[0].findall('OME:Pixels', namespaces=NS)
        assert len(pixels) == 1
        assert pixels[0].attrib['SizeX'] == '256'
        assert pixels[0].attrib['SizeY'] == '512'
        assert pixels[0].attrib['SizeZ'] == '3'
        assert pixels[0].attrib['SizeC'] == '4'
        assert pixels[0].attrib['SizeT'] == '5'
        channels = pixels[0].findall('OME:Channel', namespaces=NS)
        assert len(channels) == 0


class TestChannel(object):

    @pytest.mark.parametrize('name', [None, '', 'channel-test'])
    @pytest.mark.parametrize('color', [None, '-1', '65535'])
    def test_channel(self, tmpdir, name, color):
        f = str(tmpdir.join('3channels.companion.ome'))

        i = Image("test", 256, 512, 3, 4, 5)
        i.add_channel()
        i.add_channel(name="Blue", color="65535", samplesPerPixel=1)
        i.add_channel(name=name, color=color)
        create_companion(images=[i], out=f)

        root = ElementTree.parse(f).getroot()
        images = root.findall('OME:Image', namespaces=NS)
        assert len(images) == 1
        assert images[0].attrib['Name'] == 'test'
        pixels = images[0].findall('OME:Pixels', namespaces=NS)
        assert len(pixels) == 1
        assert pixels[0].attrib['SizeX'] == '256'
        assert pixels[0].attrib['SizeY'] == '512'
        assert pixels[0].attrib['SizeZ'] == '3'
        assert pixels[0].attrib['SizeC'] == '4'
        assert pixels[0].attrib['SizeT'] == '5'
        channels = pixels[0].findall('OME:Channel', namespaces=NS)
        assert len(channels) == 3
        assert 'Name' not in channels[0].attrib
        assert 'Color' not in channels[0].attrib
        assert channels[0].attrib['SamplesPerPixel'] == '1'
        assert channels[1].attrib['Name'] == 'Blue'
        assert channels[1].attrib['Color'] == '65535'
        assert channels[1].attrib['SamplesPerPixel'] == '1'
        if name:
            assert channels[2].attrib['Name'] == name
        else:
            assert 'Name' not in channels[2].attrib
        if color:
            assert channels[2].attrib['Color'] == color
        else:
            assert 'Color' not in channels[2].attrib
        assert channels[2].attrib['SamplesPerPixel'] == '1'

    def test_rgb_channel(self, tmpdir):
        f = str(tmpdir.join('rgb.companion.ome'))

        i = Image("test", 256, 512, 3, 4, 5)
        i.add_channel(samplesPerPixel=3)
        create_companion(images=[i], out=f)

        root = ElementTree.parse(f).getroot()
        images = root.findall('OME:Image', namespaces=NS)
        assert len(images) == 1
        assert images[0].attrib['Name'] == 'test'
        pixels = images[0].findall('OME:Pixels', namespaces=NS)
        assert len(pixels) == 1
        assert pixels[0].attrib['SizeX'] == '256'
        assert pixels[0].attrib['SizeY'] == '512'
        assert pixels[0].attrib['SizeZ'] == '3'
        assert pixels[0].attrib['SizeC'] == '4'
        assert pixels[0].attrib['SizeT'] == '5'
        channels = pixels[0].findall('OME:Channel', namespaces=NS)
        assert len(channels) == 1
        assert 'Name' not in channels[0].attrib
        assert 'Color' not in channels[0].attrib
        assert channels[0].attrib['SamplesPerPixel'] == '3'

    def test_too_many_channels(self, tmpdir):
        f = str(tmpdir.join('invalid.companion.ome'))

        i = Image("test", 512, 512, 1, 2, 1)
        i.add_channel()
        i.add_channel()
        i.add_channel()
        with pytest.raises(AssertionError):
            create_companion(images=[i], out=f)

    def test_too_many_channel_samples(self, tmpdir):
        f = str(tmpdir.join('invalid.companion.ome'))

        i = Image("test", 512, 512, 1, 2, 1)
        i.add_channel(samplesPerPixel=3)
        with pytest.raises(AssertionError):
            create_companion(images=[i], out=f)
