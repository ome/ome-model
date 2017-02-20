OME-TIFF sample data
====================

This section provides some sample data in OME-TIFF format. They include data
produced from an acquisition system as well as artificial sample datasets i.e.
designed for developer testing that illustrate some possible data
organizations, which should be useful if you are interested in implementing
support for OME-TIFF within your software.

All the OME-TIFF sample data discussed below are available from our
:ometiff_downloads:`OME-TIFF sample images resource <>`.

Biological datasets
-------------------

.. _tubhiswt_samples:

Tubhiswt
^^^^^^^^

The following OME-TIFF datasets consist of tubulin histone GFP coexpressing
*C. elegans* embryos. Many thanks to
`Josh Bembenek <http://loci.wisc.edu/people/josh-bembenek>`_ for preparing
and imaging this sample data.

The datasets were acquired on a multiphoton workstation (2.1 GHz Athlon
XP 3200+ with 1GB of RAM) using
`WiscScan <http://loci.wisc.edu/software/wiscscan>`_. All image
planes were collected at 512x512 resolution in 8-bit grayscale, with an
integration value of 2.

The files available for download have been updated to the current schema
version since their initial creation.

.. list-table::
  :header-rows: 1

  -  * Dataset (zip bundle)
     * Image dimensions (XYZCT)
     * Number of files

  -  * :ometiff_downloads:`Tubhiswt 2D <tubhiswt-2D>` (:ometiff_downloads:`tubhiswt-2D.zip <tubhiswt-2D.zip>`)
     * 512 x 512 x 1 x 2 x 1
     * 2

  -  * :ometiff_downloads:`Tubhiswt 3D <tubhiswt-3D>` (:ometiff_downloads:`tubhiswt-3D.zip <tubhiswt-3D.zip>`)
     * 512 x 512 x 1 x 2 x 20
     * 2

  -  * :ometiff_downloads:`Tubhiswt 4D <tubhiswt-4D>` (:ometiff_downloads:`tubhiswt-4D.zip <tubhiswt-4D.zip>`)
     * 512 x 512 x 10 x 2 x 43
     * 86


.. _artificial-datasets:

Artificial datasets
-------------------

5D datasets
^^^^^^^^^^^

All datasets in the following table are single OME-TIFF files generated using
Bio-Formats ``loci.formats.tools.MakeTestOmeTiff``. Each plane is labeled
according to its dimensional position for easy testing.

.. list-table::
  :header-rows: 1
  :widths: 15 15 20

  -  * Name
     * Image dimensions (XYZCT)
     * Available extensions
  
  -  * Single channel
     * 439 x 167 x 1 x 1 x 1
     * :ometiff_downloads:`ome.tif <bioformats-artificial/single-channel.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/single-channel.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/single-channel.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/single-channel.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/single-channel.ome.tf2>`

  -  * Multi channel
     * 439 x 167 x 1 x 3 x 1
     * :ometiff_downloads:`ome.tif <bioformats-artificial/multi-channel.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/multi-channel.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/multi-channel.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/multi-channel.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/multi-channel.ome.tf2>`

  -  * Z series
     * 439 x 167 x 5 x 1 x 1
     * :ometiff_downloads:`ome.tif <bioformats-artificial/z-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/z-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/z-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/z-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/z-series.ome.tf2>`

  -  * Time series
     * 439 x 167 x 1 x 1 x 7
     * :ometiff_downloads:`ome.tif <bioformats-artificial/time-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/time-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/time-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/time-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/time-series.ome.tf2>`

  -  * Multi channel Z series
     * 439 x 167 x 5 x 3 x 1
     * :ometiff_downloads:`ome.tif <bioformats-artificial/multi-channel-z-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/multi-channel-z-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/multi-channel-z-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/multi-channel-z-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/multi-channel-z-series.ome.tf2>`

  -  * Multi channel time series
     * 439 x 167 x 1 x 3 x 7
     * :ometiff_downloads:`ome.tif <bioformats-artificial/multi-channel-time-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/multi-channel-time-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/multi-channel-time-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/multi-channel-time-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/multi-channel-time-series.ome.tf2>`

  -  * 4D series
     * 439 x 167 x 5 x 1 x 7
     * :ometiff_downloads:`ome.tif <bioformats-artificial/4D-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/4D-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/4D-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/4D-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/4D-series.ome.tf2>`

  -  * Multi channel 4D series
     * 439 x 167 x 5 x 3 x 7
     * :ometiff_downloads:`ome.tif <bioformats-artificial/multi-channel-4D-series.ome.tif>`, :ometiff_downloads:`ome.tiff <bioformats-artificial/multi-channel-4D-series.ome.tiff>`, :ometiff_downloads:`ome.tf8 <bioformats-artificial/multi-channel-4D-series.ome.tf8>`, :ometiff_downloads:`ome.btf <bioformats-artificial/multi-channel-4D-series.ome.btf>`, :ometiff_downloads:`ome.tf2 <bioformats-artificial/multi-channel-4D-series.ome.tf2>`

.. _modulo-datasets:

Modulo datasets
^^^^^^^^^^^^^^^

Sample files implementing the :doc:`/developers/6d-7d-and-8d-storage` are
available from the :ometiff_downloads:`modulo` folder of the image downloads
resource.

.. list-table::
  :widths: 25 15 40
  :header-rows: 1

  -  * Name
     * Image dimensions (XYZCT)
     * Modulo description

  -  * :ometiff_downloads:`SPIM-ModuloAlongZ.ome.tiff <modulo/SPIM-ModuloAlongZ.ome.tiff>`
     * 160 x 220 x 8 x 2 x 12
     * 4 tiles interleaved as ModuloAlongT each recorded at 4 angles
       interleaved as ModuloAlongZ

  -  * :ometiff_downloads:`LAMBDA-ModuloAlongZ-ModuloAlongT.ome.tiff <modulo/LAMBDA-ModuloAlongZ-ModuloAlongT.ome.tiff>`
     * 200 x 200 x 5 x 1 x 10
     * excitation of 5 wavelength [Λ, big-lambda] interleaved as ModuloAlongZ,
       each recorded at 10 emission wavelength ranges [λ, lambda] interleaved
       as ModuloAlongT

  -  * :ometiff_downloads:`FLIM-ModuloAlongT-TSCPC.ome.tiff <modulo/FLIM-ModuloAlongT-TSCPC.ome.tiff>`
     * 180 x 220 x 1 x 2 x 16
     * 2 channels and 8 histogram bins each recorded at 2 'real-time' points T,
       with additional relative-time points (time relative to the
       excitation pulse) interleaved as ModuloAlongT

  -  * :ometiff_downloads:`FLIM-ModuloAlongC.ome.tiff <modulo/FLIM-ModuloAlongC.ome.tiff>`
     * 180 x 150 x 1 x 16 x 1
     * 2 real channels and 8 histogram bins each recorded at 2 timepoints, with
       additional relative-time points interleaved between channels as
       ModuloAlongC

.. _multifile_samples:

Multi-file OME-TIFF filesets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section lists various examples of OME-TIFF datasets distributed across multiple TIFF files. Both datasets contain a set of 18 by 24 pixel images with black and white text on each plane giving its time, z-depth and channel. Each of the five focal planes is saved as a separate OME-TIFF named :file:`multifile-Zxx.ome.tiff` where `xx` is the index of the focal plane.

.. list-table::
  :header-rows: 1

  -  * Dataset
     * Image dimensions (XYZCT)
     * Full metadata file*
     * Partial metadata files†

  -  * :ometiff_downloads:`Master OME-TIFF fileset <binaryonly>`
     * 18 x 24 x 5 x 1 x 1
     * :file:`multifile-Z1.ome.tiff`
     * :file:`multifile-Z[2-5].ome.tiff`

  -  * :ometiff_downloads:`Companion OME-XML fileset <companion>`
     * 18 x 24 x 5 x 1 x 1
     * :file:`multifile.companion.ome`
     * :file:`multifile-Z[1-5].ome.tiff`

\*
  The full OME-XML metadata describing the whole fileset is either embedded
  into an OME-TIFF or stored in a companion OME-XML file
†
  Partial OME-XML metadata blocks are embedded into the OME-TIFF files
  and refer to the file containing the full OME-XML metadata as described
  in the :ref:`specification <binary_only>`.
