OME-XML Java library
====================


The OME-XML Java library is a collection of Java packages for
manipulating OME-XML metadata structures. The OME-XML Java library's
metadata processing facilities form the backbone of the
:bf:`Bio-Formats <>` library's support for OME-XML conversion.

Download
--------

The ``ome-xml`` artifacts are hosted on the
`Maven Central Repository <https://search.maven.org/>`_ under the group ``org.openmicroscopy`` and distributed under the
`2-Clause BSD license <https://opensource.org/licenses/BSD-2-Clause>`_.

Installation
------------

To use, add **ome-xml.jar** to your classpath or build path.

Usage
-----

Refer to the :javadoc:`online API documentation <>`, specifically the
ome.xml.\* packages. For an example of usage, see the
:bf_source:`Screen Plate Well unit test <components/formats-bsd/test/loci/formats/utests/SPWModelMock.java>`.

The OMENode is the root ("OME") node of the OME-XML. Each XML element
has its own node type (e.g. "Image" has ImageNode) with its own
accessor and mutator methods, to make navigation of the OME-XML
structure easier than it would be with a raw DOM object. However, there
are some limitations to what can be done with the API. If your
application needs access to a node's backing DOM element to work with it
directly, you can call ``getDOMElement()`` on a node.

Source code
-----------

The OME-XML Java library is an open source project—the source code is
freely accessible via the https://github.com/ome/ome-model Git repository.

