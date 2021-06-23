#!/usr/bin/env python
# Generate companion files

import re
import sys
import uuid
import xml.etree.ElementTree as ET
from . import __version__

OME_ATTRIBUTES = {
    'Creator': "ome_model %s" % __version__,
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
                 name=None,
                 color=None,
                 samplesPerPixel=1,
                 ):
        self.data = {
            'ID': 'Channel:%s' % self.ID,
            'SamplesPerPixel': str(samplesPerPixel),
        }
        if name:
            self.data["Name"] = name
        if color:
            self.data["Color"] = str(color)
        Channel.ID += 1


class Plane(object):

    ALLOWED_KEYS = (
        'DeltaT', 'DeltaTUnit', 'ExposureTime', 'ExposureTimeUnit',
        'PositionX', 'PositionXUnit', 'PositionY', 'PositionYUnit',
        'PositionZ', 'PositionZUnit')

    def __init__(self, TheC=0, TheZ=0, TheT=0, options={}):
        self.data = {
            'TheC': str(TheC),
            'TheZ': str(TheZ),
            'TheT': str(TheT),
        }
        if options:
            for key, value in options.items():
                if key in self.ALLOWED_KEYS:
                    self.data[key] = value


class UUID(object):
    def __init__(self,
                 filename=None
                 ):
        self.data = {"FileName": filename}
        self.value = "urn:uuid:%s" % str(uuid.uuid4())


class TiffData(object):
    def __init__(self,
                 firstC=0,
                 firstT=0,
                 firstZ=0,
                 ifd=None,
                 planeCount=None,
                 uuid=None
                 ):
        self.data = {
            "FirstC": str(firstC),
            "FirstT": str(firstT),
            "FirstZ": str(firstZ)
        }
        self.uuid = uuid
        if ifd:
            self.data["IFD"] = str(ifd)
        if planeCount:
            self.data["PlaneCount"] = str(planeCount)


class Image(object):

    ID = 0

    def __init__(self,
                 name,
                 sizeX, sizeY, sizeZ, sizeC, sizeT,
                 tiffs=None,
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
            'TIFFs': [],
            'Planes': [],
        }
        Image.ID += 1
        if tiffs:
            for tiff in tiffs:
                self.add_tiff(tiff)

    def add_channel(self, name=None, color=None, samplesPerPixel=1):
        self.data["Channels"].append(
            Channel(
                self, name=name, color=color, samplesPerPixel=samplesPerPixel
            ))

    def add_tiff(self, filename, c=0, t=0, z=0, ifd=None, planeCount=None):

        if c is None and t is None and z is None:
            # If no mapping specified, assume single plane TIFF which name
            # contain the z,c,t indices
            c, t, z = parse_tiff(filename)
        self.data["TIFFs"].append(TiffData(
            firstC=c,
            firstT=t,
            firstZ=z,
            ifd=ifd,
            planeCount=planeCount,
            uuid=UUID(filename)))

    def add_plane(self, c=0, t=0, z=0, options={}):
        assert c >= 0 and c < int(self.data['Pixels']['SizeC'])
        assert z >= 0 and z < int(self.data['Pixels']['SizeZ'])
        assert t >= 0 and t < int(self.data['Pixels']['SizeT'])
        self.data["Planes"].append(Plane(
            TheC=c, TheT=t, TheZ=z, options=options))

    def validate(self):
        sizeC = int(self.data["Pixels"]["SizeC"])
        assert (len(self.data["Channels"]) <= sizeC), str(self.data)
        channel_samples = sum([int(x.data['SamplesPerPixel'])
                              for x in self.data["Channels"]])
        assert channel_samples <= sizeC, str(self.data)
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


def create_companion(plates=None, images=None, out=None):
    """
    Create a companion OME-XML for a given experiment.
    Assumes 2D TIFFs
    """
    root = ET.Element("OME", attrib=OME_ATTRIBUTES)
    if not plates:
        plates = []
    if not images:
        images = []

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

        for tiff in i["TIFFs"]:
            tiffdata = ET.SubElement(pixels, "TiffData", attrib=tiff.data)
            if tiff.uuid:
                ET.SubElement(
                    tiffdata, "UUID", tiff.uuid.data).text = tiff.uuid.value

        for plane in i["Planes"]:
            ET.SubElement(pixels, "Plane", attrib=plane.data)

    # https://stackoverflow.com/a/48671499/56887
    kwargs = dict(encoding="UTF-8")
    kwargs["xml_declaration"] = True
    if not out:
        try:
            out = sys.stdout.buffer
        except AttributeError:
            # ipykernel.iostream.OutStream (used by Jupyter Notebook) does not
            # have a .buffer attribute
            out = sys.stdout
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
