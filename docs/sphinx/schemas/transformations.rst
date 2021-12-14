Transformations
===============

Available transformations
-------------------------

====================== ========== ==================
Available transforms   Direction  Status
====================== ========== ==================
2003-FC-to-2007-06.xsl upgrade    excellent
2003-FC-to-2008-09.xsl upgrade    excellent
2007-06-to-2008-02.xsl upgrade    excellent
2007-06-to-2008-09.xsl upgrade    excellent
2008-02-to-2008-09.xsl upgrade    excellent
2008-09-to-2009-09.xsl upgrade    excellent
2009-09-to-2010-04.xsl upgrade    excellent
2010-04-to-2010-06.xsl upgrade    excellent
2010-06-to-2011-06.xsl upgrade    excellent
2011-06-to-2012-06.xsl upgrade    excellent
2012-06-to-2013-06.xsl upgrade    excellent
2013-06-to-2015-01.xsl upgrade    excellent
2015-01-to-2016-06.xsl upgrade    excellent
2010-06-to-2003-FC.xsl downgrade  poor (very lossy)
2010-06-to-2008-02.xsl downgrade  fair (lossy)
2011-06-to-2010-06.xsl downgrade  good
2012-06-to-2011-06.xsl downgrade  good
2013-06-to-2012-06.xsl downgrade  good
2015-01-to-2013-06.xsl downgrade  good
2016-06-to-2015-01.xsl downgrade  good
====================== ========== ==================

Quality of transformations
--------------------------

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   * - Target / Source
     - 2003-FC
     - 2007-06
     - 2008-02
     - 2008-09
     - 2009-09
     - 2010-04
     - 2010-06
     - 2011-06
     - 2012-06
     - 2013-06
     - 2015-01
     - 2016-06
   * - 2003-FC
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2007-06
     - poor
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2008-02
     - poor
     - poor
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2008-09
     - poor
     - poor
     - poor
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2009-09
     - poor
     - poor
     - poor
     - poor
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2010-04
     - poor
     - poor
     - poor
     - fair
     - fair
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2010-06
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     -
     - excellent
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2011-06
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     - good
     -
     - excellent
     - excellent
     - excellent
     - excellent
   * - 2012-06
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     - good
     - good
     -
     - excellent
     - excellent
     - excellent
   * - 2013-06
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     - good
     - good
     - good
     -
     - excellent
     - excellent
   * - 2015-01
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     - good
     - good
     - good
     - good
     -
     - excellent
   * - 2016-06
     - poor
     - poor
     - fair
     - fair
     - fair
     - fair
     - good
     - good
     - good
     - good
     - good
     -

Key to quality
--------------

-  **poor** (very lossy) - the bare minimum of metadata is preserved to
   allow image display, all other metadata is lost
-  **fair** (lossy) - a portion of the metadata is preserved, at least
   enough to display the image and some other data, it will be far from
   complete however
-  **good** - most information is preserved, it may be possible to do a
   better job but could be difficult for technical reasons or require
   custom code not just a transform
-  **excellent** - as much information as possible is preserved, some
   values can still be lost if there are completely incompatible with
   the new schema

