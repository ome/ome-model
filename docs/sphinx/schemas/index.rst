Schema version information
==========================


.. only:: html

    - :doc:`june-2016-2`
    - :doc:`june-2016`
    - :doc:`january-2015`
    - :doc:`june-2013`
    - :doc:`june-2012`
    - :doc:`june-2011`
    - :doc:`june-2010`
    - :doc:`april-2010`
    - :doc:`september-2009`
    - :doc:`september-2008`
    - :doc:`february-2008`
    - :doc:`june-2007-2`
    - :doc:`june-2007`


Information on the version structure
------------------------------------

All of the schema files released since 2007 have used a new
versioning system. This is composed of two parts, Major and Minor.

Major
^^^^^

The major part of a version is contained in the namespace of each
schema. This consists of the month and year the schema was first
released. The format for the new URI for the namespace will be

::

    http://www.openmicroscopy.org/Schemas/[NameSpaceTitle]/[YearAsFourDigits]-[MonthAsTwoDigits]

This means the June 2016 major release for the OME schema uses the
namespace

::

    http://www.openmicroscopy.org/Schemas/OME/2016-06/

and that the schema file will be located at

::

    http://www.openmicroscopy.org/Schemas/OME/2016-006/ome.xsd

There will be a consultation period before each major release. Major releases
may include breaking changes.

Minor
^^^^^

In the schema element of the XSD file, there is a version attribute:

::

    <xsd:schema xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
        …
        version="1" 
        … >

This is used to record the minor version number of the schema. This
starts at 1 and counts up in integers (1, 2, 3 etc.) with each minor
version.

A new minor version is used for small non-breaking changes. If a change
is more significant, or would break application relying on the current
schema, then it must be a major version.

Minor versions will be released as needed.

Examples and consequences
^^^^^^^^^^^^^^^^^^^^^^^^^

The relationship between a major and minor version has been set up as
follows. Any file written by an application conforming to a major
version, will always continue to be valid under any minor version update
to the schema. The first releases to make use of the major and minor 
system were June 2007(Major) and September 2007(Minor).
If microscope application X saves a file using the major
June 2007 version of OME-XML, then that file can be read by any
application that understands either the June 2007 major version or the
September 2007 minor version. The main consequence of this approach is
that file readers have to be kept up to date or have to be written in a
way that allows some flexibility.

An example of a minor change is the serial number in the manufacture
specification. In the June 2007 major version, a SerialNumber is
required in ManafactSpec. It was decided to make this optional as it
was not always available to a file writer. This is a minor change as the new 
file can still validate whether it is present or absent.

An example of a major change is the moving of ImageRef from the SPW.xsd
file to the ome.xsd file. This change had been proposed as it is
envisaged that in the future ImageRef will be used outside the
Screen/Plate/Well model, so it belongs in the same namespace as
Image. As any reference to SPW:ImageRef would then have to
become OME:ImageRef, this causes validation errors in files
following the June 2007 schema and is therefore a new major version.

Technical schema descriptions
-----------------------------

Auto-generated documentation is available for each release of the
schema, including information on each attribute and element. These are
published as :schema:`XSD files <>` on the OME website. They are usually
read by XML validators and parsers but are viewable as text files.
Alternatively, you can browse the
:schema_doc:`current version of the entire Schema <ome.html>` online.

Transforms are available which convert between the the different versions
of the schemas.
