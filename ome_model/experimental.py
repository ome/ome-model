#!/usr/bin/env python
# Generate companion files

import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET


OME_ATTRIBUTES = {
    'xmlns': 'http://www.openmicroscopy.org/Schemas/OME/2016-06',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xmlns:OME': 'http://www.openmicroscopy.org/Schemas/OME/2016-06',
    'xsi:schemaLocation': 'http://www.openmicroscopy.org/Schemas/OME/2016-06 \
http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd',
}

TIFF_PARSER = "^.*?" # Ignore prefix
TIFF_PARSER += "(?:[-_]+|"  # Skip separators
TIFF_PARSER += "[Cc]_?(?P<channel>[^-_]+)|"  # Channel section
TIFF_PARSER += "[TtHhRr]_?(?P<time>[^-_]+)|"  # "Time" section
TIFF_PARSER += "[Zz]_?(?P<slice>[^-_]+)"  # Z-slices
TIFF_PARSER += ")+"  # As many of those three as needed
TIFF_PARSER += ".*?[.].*?" # Ignore the rest, but don't slurp the file ending
TIFF_PARSER = re.compile(TIFF_PARSER)


class Channel(object):

    ID = 0

    def __init__(self,
        image,
        name,
        color,
        samplesPerPixel=1,
    ):
        self.data = {
            'ID': 'Channel:%s:%s' % (image, self.ID),
            'Name': name,
            'Color': str(color),
            'SamplesPerPixel': str(samplesPerPixel),
        }
        self.ID += 1


class Image(object):

    ID = 0

    def __init__(self,
        name,
        sizeX, sizeY, sizeZ, sizeC, sizeT,
        tiffs,
        order="XYZTC",
        type="uint16",
    ):
        self.data = {
            'Image': {'ID': 'Image:%s' % self.ID, 'Name': name},
            'Pixels': {
                'ID': 'Pixels:%s:%s' % (self.ID, self.ID),
                'DimensionOrder': order,
                'Type': type,
                'SizeX': str(sizeX),
                'SizeY': str(sizeY),
                'SizeZ': str(sizeZ),
                'SizeT': str(sizeT),
                'SizeC': str(sizeC),
            },
            'Channels': [],
            'TIFFData': tiffs,
        }
        Image.ID += 1

    def add_channel(self, name, color, samplesPerPixel=1):
        self.data["Channels"].append(
            Channel(
                self, name, color, samplesPerPixel
            ))

    def validate(self):
        assert len(self.data["Channels"]) == int(self.data["Pixels"]["SizeC"]), \
               str(self.data)
        return self.data


def parse_tiff(tiff):
    """
    Extracts (c, t, z) from a tiff filename.
    """
    m = TIFF_PARSER.match(tiff)
    return (m.group("channel"), m.group("time"), m.group("slice"))


def create_companion(images):
    """
    Create a companion OME-XML for a given experiment.
    Assumes 2D TIFFs
    """
    root = ET.Element("OME", attrib=OME_ATTRIBUTES)
    for img in images:
        i = img.validate()
        image = ET.SubElement(root, "Image", attrib=i["Image"])
        pixels = ET.SubElement(image, "Pixels", attrib=i["Pixels"])
        for channel in i["Channels"]:
            c = channel.data  # TODO: validation?
            ET.SubElement(pixels, "Channel", attrib=c)

        tiffs = i["TIFFData"]
        for tiff in tiffs:
            c, t, z = parse_tiff(tiff)
            tiffdata = ET.SubElement(pixels, "TiffData", attrib={
                "FirstC": c,
                "FirstT": t,
                "FirstZ": z,
                "PlaneCount": "1",
                "IFD": '0'})
            ET.SubElement(tiffdata, "UUID", attrib={
                "FileName": tiff}).text = str(uuid.uuid4())

    # https://stackoverflow.com/a/48671499/56887
    xmlstr = ET.tostring(root).decode()
    sys.stdout.write(xmlstr)


def fake_image():
    tiffs = [
        "foo_c0_t0_z0.tiff",
        "bar_t0_c1_z0.tiff",
        "baz_z0_t0_c2.tiff",
    ]
    image = Image("test", 64, 64, 1, 3, 1, tiffs)
    image.add_channel("red", 0)
    image.add_channel("green", 0)
    image.add_channel("blue", 0)
    return image


if __name__ == "__main__":
    image = fake_image()
    create_companion([image])
