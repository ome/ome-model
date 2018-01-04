The OME-TIFF format
===================

The OME-TIFF format was created to
maximize the respective strengths of OME-XML and TIFF. It takes advantage
of the rich metadata defined in OME-XML while retaining the pixels in
multi-page TIFF format for compatibility with many more applications.

Characteristics
---------------

An OME-TIFF dataset has the following characteristics:

#. Image planes are stored within one multi-page TIFF file, or across
   multiple TIFF files. Any image organization is feasible.
#. A complete OME-XML metadata block describing the dataset is embedded
   in each TIFF file's header. Thus, even if some of the TIFF files in a
   dataset are misplaced, the metadata remains intact.
#. The OME-XML metadata block may contain anything allowed in a standard
   OME-XML file.
#. OME-TIFF uses the standard TIFF mechanism for storing one or more image
   planes in each of the constituent files, instead of encoding pixels as
   base64 chunks within the XML. Since TIFF is an image
   format, it makes sense to only use OME-TIFF as opposed to OME-XML, when
   there is at least one image plane.

Support
-------

OME-TIFF is supported by:

* `Accelrys Inc. <http://accelrys.com/>`_
* `GE Healthcare Life Sciences (formerly Applied Precision) <https://www.gelifesciences.com>`_
* `Bitplane AG <http://www.bitplane.com/>`_
* `Carl Zeiss Microscopy GmbH <https://www.zeiss.com/microscopy/int/home.html>`_
* `Definiens <http://www.definiens.com>`_
* `DRVision Technologies LLC <https://www.drvtechnologies.com>`_
* `iMagic <http://www.imagic.ch/index.php?id=15&L=2/>`_
* `Intelligent Imaging Innovations, Inc. <https://www.intelligent-imaging.com>`_
* `Leica Inc. <https://www.leica-microsystems.com/>`_
* `Mayachitra Inc. <http://mayachitra.com/>`_
* `Micro-Manager <https://micro-manager.org/wiki/>`_
* `Molecular Devices Inc. <https://www.moleculardevices.com>`_
* `PerkinElmer <http://www.perkinelmer.com/>`_
* `Scientifica <http://www.scientifica.uk.com>`_
* `Scientific Volume Imaging B.V. <https://svi.nl/HomePage>`_
* `Strand Life Sciences <http://strandls.com>`_
* `TILL Photonics GmbH, now FEI Munich <https://www.fei.com/home/>`_

Public image repositories allowing image downloads as OME-TIFF
--------------------------------------------------------------

* `ASCB CELL Image Library <http://www.cellimagelibrary.org/>`_
* `Harvard Medical School LINCS Project <http://lincs.hms.harvard.edu/>`_
* `JCB DataViewer <http://jcb-dataviewer.rupress.org/>`_
* `Stowers Institute Original Data Repository <http://www.stowers.org/research/publications/odr>`_

|

.. only:: html

    For detailed technical information on OME-TIFF, see the 
    :doc:`specification`.

    There is further information about :doc:`tools` available.

    We also have some :doc:`example code <code>` in Java for
    extracting and modifying TIFF comments and converting other file formats 
    to OME-TIFF.

    Lastly, some :doc:`data` is available for
    download, along with statistics comparing OME-TIFF and OME-XML with
    various types of compression.

