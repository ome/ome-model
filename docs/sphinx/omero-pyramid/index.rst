The OMERO pyramid format
========================

The OMERO pyramid format is a way of storing very large images for easier visualization.
Currently only v1.0.0 is defined.

.. seealso::

  :bf_doc:`Working with whole slide images <developers/wsi.html>`

v1.0.0
------

The OMERO pyramid format is a :bf_doc:`TIFF <formats/tiff.html>` file containing JPEG-2000 compressed image tiles.  All resolutions for a tile
are encoded in the same JPEG-2000 stream, using the "decompression levels" feature of JPEG-2000.
As a result, only data types supported by the JPEG-2000 standard (``uint8`` and ``uint16``) are supported.
Images with pixel type ``uint32``, ``float`` (32-bit floating point), or ``double`` (64-bit floating point) cannot be converted to
an OMERO pyramid.  Pyramid files larger than 4 gigabytes are supported, as are pyramids containing multiple channels,
Z sections, and/or timepoints.

Each pyramid contains multiple resolutions for each image plane, with each resolution stored in descending order from largest to smallest XY size.
Each resolution is half the width and height of the previous resolution.  OMERO by default writes 5 resolutions, but this is an implementation
detail and not a limitation of the file format.

One IFD is required to be stored for each image plane, but every resolution for a given plane is encapsulated in that plane's single IFD.
Additional IFDs for each resolution are not expected; any IFDs that do not represent a JPEG-2000 stream with multiple decompression
levels will be ignored.
