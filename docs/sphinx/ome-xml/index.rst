The OME-XML format
==================

OME-XML is a `file format <https://en.wikipedia.org/wiki/File_format>`_
for storing microscopy information (both pixels and metadata) using the
OME-XML data model.

.. note:: OME-XML as a file format is superseded by OME-TIFF, which 
    is the preferred container format for image data making use of the
    OME Data Model.

The purpose of OME-XML is to provide a rich, extensible way to save
information concerning microscopy experiments and the images acquired
therein, including:

-  dimensional parameters defining the scope of the image pixels
   (e.g. resolution, number of focal planes, number of time points, number of
   channels)
-  the hardware configuration used to acquire the image planes
   (e.g. microscope, detectors, lenses, filters)
-  the settings used with said hardware (e.g. physical size of the image
   planes in microns, laser gain and offset, channel configuration)
-  the person performing the experiment
-  some details regarding the experiment itself, such as a description,
   the type of experiment (e.g. FRET, time lapse, fluorescence lifetime)
   and events occurring during acquisition (e.g. laser ablation, stage
   motion)
-  additional custom information you may wish to provide about your
   experiment in a structured form (known as 
   :doc:`/developers/structured-annotations`)


Features and applications
-------------------------

The OME-XML file serves as a convenient file format for data migration
from one site or user to another. The OME-XML file captures all image
acquisition and experimental metadata, along with the binary image data,
and packages it into an easily readable package. The
`paper <https://genomebiology.biomedcentral.com/articles/10.1186/gb-2005-6-5-r47>`_
describing the design and implementation of the OME-XML file appeared in
Genome Biology.

.. note::

    OME-XML files can be read by potentially any software package - you
    do not need OME image management software to use OME-XML.

Some specific features of the OME-XML file format:

-  OME-XML files may contain one or more sets of 5-D pixels, for example
   raw data from a microscope, the deconvolved data, and a volume
   rendered view.
-  OME-XML files contain all the metadata associated with an image,
   including the experimental (e.g. cells, genes) and acquisition
   (e.g. microscope light sources, filters, detectors)
   metadata.
-  OME-XML Image pixels may be stored compressed directly in
   XML with base64 encoding. Compression of the pixels and the metadata
   is supported through widely-available patent-free compression schemes
   (gzip and bzip2). OME-XML Images are addressable by plane.
-  OME-XML files have a built-in mechanism for supporting arbitrary
   user-defined data that can be used globally or attached to Images,
   Features (objects inside Images), and Datasets. Mechanisms for
   OME-compliant systems to populate databases with these user-defined
   fields is part of the specification. See the 
   :doc:`/developers/structured-annotations` XML Schema section.

The OME-XML Schema .xsd files and technical documentation are available on the 
:schema:`Schema pages <>`.


Migrating or sharing data with OME-XML
--------------------------------------

Data saved in an OME-XML file is easily read by any software capable of
reading and interpreting XML. OME software tools can export and
import OME-XML files, but any software capable of reading XML may be used.
