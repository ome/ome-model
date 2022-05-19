Transformations
===============

Available transformations
-------------------------

.. list-table::
   :header-rows: 1

   * - Available transforms
     - Direction
     - Status
   * - :schema:`2003-FC-to-2007-06.xsl <Transforms/2016-06-to-2015-01.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2003-FC-to-2008-09.xsl <Transforms/2003-FC-to-2008-09.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2007-06-to-2008-02.xsl <Transforms/2007-06-to-2008-02.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2007-06-to-2008-09.xsl <Transforms/2007-06-to-2008-09.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2008-02-to-2008-09.xsl <Transforms/2008-02-to-2008-09.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2009-09-to-2010-04.xsl <Transforms/2009-09-to-2010-04.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2010-04-to-2010-06.xsl <Transforms/2010-04-to-2010-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2010-04-to-2010-06.xsl <Transforms/2010-04-to-2010-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2010-06-to-2011-06.xsl <Transforms/2010-06-to-2011-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2011-06-to-2012-06.xsl <Transforms/2011-06-to-2012-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2012-06-to-2013-06.xsl <Transforms/2012-06-to-2013-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2013-06-to-2015-01.xsl <Transforms/2013-06-to-2015-01.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2015-01-to-2016-06.xsl <Transforms/2015-01-to-2016-06.xsl>`
     - upgrade
     - :term:`excellent`
   * - :schema:`2010-06-to-2003-FC.xsl <Transforms/2010-06-to-2003-FC.xsl>`
     - downgrade
     - :term:`poor`
   * - :schema:`2010-06-to-2008-02.xsl <Transforms/2010-06-to-2008-02.xsl>`
     - downgrade
     - :term:`fair`
   * - :schema:`2011-06-to-2010-06.xsl <Transforms/2011-06-to-2010-06.xsl>`
     - downgrade
     - :term:`good`
   * - :schema:`2012-06-to-2011-06.xsl <Transforms/2012-06-to-2011-06.xsl>`
     - downgrade
     - :term:`good`
   * - :schema:`2013-06-to-2012-06.xsl <Transforms/2013-06-to-2012-06.xsl>`
     - downgrade
     - :term:`good`
   * - :schema:`2015-01-to-2013-06.xsl <Transforms/2015-01-to-2013-06.xsl>`
     - downgrade
     - :term:`good`
   * - :schema:`2016-06-to-2015-01.xsl <Transforms/2016-06-to-2015-01.xsl>`
     - downgrade
     - :term:`good`

Quality of transformations
--------------------------

.. figure:: /images/transformations_quality.png
   :align: center
   :alt: Quality of transformations

Key to quality
--------------

.. glossary::

    :term:`poor`
        the bare minimum of metadata is preserved to allow image display, all
        other metadata is lost

    :term:`fair`
        a portion of the metadata is preserved, at least enough to display the
        image and some other data, it will be far from complete however

    :term:`good`
        most information is preserved, it may be possible to do a better job
        but could be difficult for technical reasons or require custom code
        not just a transform

    :term:`excellent`
        as much information as possible is preserved, some values can still be
        lost if there are completely incompatible with the new schema
