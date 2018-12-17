#!/usr/bin/env python
# Generate companion files

from __future__ import print_function
import re
import sys
import uuid
import xml.etree.ElementTree as ET

if sys.version_info[0] > 2:
    PYTHON = 3
else:
    PYTHON = 2

OME_ATTRIBUTES = {
    'Creator': "ome_model/experimental.py",
    'UUID': "urn:uuid:%s" % uuid.uuid4(),
    'xmlns': 'http://www.openmicroscopy.org/Schemas/OME/2016-06',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsi:schemaLocation': 'http://www.openmicroscopy.org/Schemas/OME/2016-06 \
http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd',
}

TIFF_PARSER = "^.*?"  # Ignore prefix
TIFF_PARSER += "(?:[-_]+|"  # Skip separators
TIFF_PARSER += "[Cc]_?(?P<channel>[^-_]+)|"  # Channel section
TIFF_PARSER += "[TtHhRr]_?(?P<time>[^-_]+)|"  # "Time" section
TIFF_PARSER += "[Zz]_?(?P<slice>[^-_]+)"  # Z-slices
TIFF_PARSER += ")+"  # As many of those three as needed
TIFF_PARSER += ".*?[.].*?"  # Ignore the rest, but don't slurp the file ending
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
            'ID': 'Channel:%s' % self.ID,
            'Name': name,
            'Color': str(color),
            'SamplesPerPixel': str(samplesPerPixel),
        }
        Channel.ID += 1


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
        assert (len(self.data["Channels"]) ==
                int(self.data["Pixels"]["SizeC"])), str(self.data)
        return self.data


class Plate(object):

    ID = 0

    def __init__(self, name, rows, columns):
        self.data = {
            'Plate': {'ID': 'Plate:%s' % self.ID, 'Name': name},
            'Wells': [],
        }
        Plate.ID += 1

    def add_well(self, row, column):
        well = Well(self, row, column)
        self.data["Wells"].append(well)
        return well


class Well(object):

    ID = 0

    def __init__(self, plate, row, column):
        self.data = {
            'Well': {
                'ID': 'Well:%s' % self.ID,
                'Row': '%s' % row,
                'Column': '%s' % column
            },
            'WellSamples': [],
        }
        Well.ID += 1

    def add_wellsample(self, index, image):
        wellsample = WellSample(self, index, image)
        self.data["WellSamples"].append(wellsample)
        return wellsample


class WellSample(object):

    ID = 0

    def __init__(self, well, index, image):
        self.data = {
            'WellSample': {
                'ID': 'WellSample:%s' % self.ID,
                'Index': '%s' % index,
            },
            'Image': image,
        }
        WellSample.ID += 1


def parse_tiff(tiff):
    """
    Extracts (c, t, z) from a tiff filename.
    """
    m = TIFF_PARSER.match(tiff)
    return (m.group("channel"), m.group("time"), m.group("slice"))


def create_companion(plates=[], images=[], out=None):
    """
    Create a companion OME-XML for a given experiment.
    Assumes 2D TIFFs
    """
    root = ET.Element("OME", attrib=OME_ATTRIBUTES)

    for plate in plates:
        p = ET.SubElement(root, "Plate", attrib=plate.data['Plate'])
        for well in plate.data["Wells"]:
            w = ET.SubElement(p, "Well", attrib=well.data["Well"])
            for wellsample in well.data["WellSamples"]:
                ws = ET.SubElement(w, "WellSample",
                                   attrib=wellsample.data['WellSample'])
                image = wellsample.data['Image']
                images.append(image)
                ET.SubElement(ws, "ImageRef", attrib={
                    "ID": image.data['Image']["ID"]})

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
                "FileName": tiff}).text = "urn:uuid:%s" % str(uuid.uuid4())

    # https://stackoverflow.com/a/48671499/56887
    kwargs = dict(encoding="UTF-8")
    out = sys.stdout
    if PYTHON >= 3:
        kwargs["xml_declaration"]=True
        out = sys.stdout.buffer
    ET.ElementTree(root).write(out, **kwargs)


def fake_image(basename="test", sizeX=64, sizeY=64, sizeZ=1, sizeC=3, sizeT=1):
    tiffs = ["%s_z%s_c%s_t%s.tiff" % (basename, z, c, t)
             for z in range(sizeZ) for c in range(sizeC)
             for t in range(sizeT)]
    image = Image("test", sizeX, sizeY, sizeZ, sizeC, sizeT, tiffs)
    image.add_channel("red", 0)
    image.add_channel("green", 0)
    image.add_channel("blue", 0)
    return image


def fake_plate(rows=2, columns=2, fields=1):

    plate = Plate("test", rows, columns)
    for row in range(rows):
        for column in range(columns):
            well = plate.add_well(row, column)
            for field in range(fields):
                basename = "Well%s%s" % (chr(row + 65), column)
                image = fake_image(basename=basename)
                well.add_wellsample(field, image)
    return plate


if __name__ == "__main__":
    plates = [fake_plate()]
    create_companion(plates=plates)
