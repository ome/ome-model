## 6.1.0 (2020-04-07)

### Python 3 support

* Update code-generation for building on Python 3.6, 3.7 [#65](https://github.com/ome/ome-model/pull/65)
* Add support for Python 3.8 and make code-generation Python 3 only [#105](https://github.com/ome/ome-model/pull/105)
* Uncap Sphinx version [#109](https://github.com/ome/ome-model/pull/109)

### OME-XML

* Add getters and setters for OME@Creator attribute for ome.xml.metadata interfaces and implementations [#108](https://github.com/ome/ome-model/pull/108)

### C++

* Remove unmaintained C++ OME-XML implementation [#111](https://github.com/ome/ome-model/pull/111)

## 6.0.1 (2019-05-09)

### Java

* Fix cyclic dependency between specification and ome-xml modules [#101](https://github.com/ome/ome-model/pull/101)

## 6.0.0 (2019-02-13)


### OME-TIFF

* Add sub-resolution support to the OME-TIFF specification [#98](https://github.com/ome/ome-model/pull/98)
* Add references to public OME-TIFF sub-resolution sample datasets [#99](https://github.com/ome/ome-model/pull/99)
* Documentation and linkchecker improvements [#70](https://github.com/ome/ome-model/pull/70) [#76](https://github.com/ome/ome-model/pull/76) [#83](https://github.com/ome/ome-model/pull/83) [#94](https://github.com/ome/ome-model/pull/94)

### Java

* Require JDK 8 as the minimum version [90](https://github.com/ome/ome-model/pull/90) [95](https://github.com/ome/ome-model/pull/95)
* MetadaConverter: add API for copying Channel metadata [#88](https://github.com/ome/ome-model/pull/88)
* Add createRotationTransform static method to AffineTransform [#77](https://github.com/ome/ome-model/pull/77)
* Build system: update Maven plugin versions [#74](https://github.com/ome/ome-model/pull/74)

### C++

* Aggregate generated C++ source files for model and enums [#79](https://github.com/ome/ome-model/pull/79)
* Require C++ 14 support [#76](https://github.com/ome/ome-model/pull/75)
* Add createRotationTransform static method to AffineTransform [#77](https://github.com/ome/ome-model/pull/77)

### Python

* Add experimental OME-XML generation Python API [#91](https://github.com/ome/ome-model/pull/91) [#92](https://github.com/ome/ome-model/pull/92) [#96](https://github.com/ome/ome-model/pull/96) [#97](https://github.com/ome/ome-model/pull/97)


5.6.3 (2018-03-13)
------------------

* Build system: update Maven plugin versions and unify property names [#53](https://github.com/ome/ome-model/pull/53) [#69](https://github.com/ome/ome-model/pull/69)

5.6.2 (2018-01-25)
------------------

* Report numerical value domain errors more clearly
  [#68](https://github.com/ome/ome-model/pull/68)

5.6.1 (2018-01-17)
------------------

Documentation updates:

* Update documentation links to use new docs.openmicroscopy.org URLs
  [#61](https://github.com/ome/ome-model/pull/61)
* Clarify and update OME-XML documentation, including removing references to
  OME-XML as a data model [#64](https://github.com/ome/ome-model/pull/64)
* Fix Leica Microsystems URL [#63](https://github.com/ome/ome-model/pull/63)
  [#66](https://github.com/ome/ome-model/pull/66)

5.6.0 (2017-12-01)
------------------

* Use C++11 `<thread>` and `<mutex>`
  [#45](https://github.com/ome/ome-model/pull/45)
* Re-add support for Boost 1.53
  [#51](https://github.com/ome/ome-model/pull/51)
* Add support for Boost 1.65.1 [#52](https://github.com/ome/ome-model/pull/52)
* Update CMake requirements to 3.4
  [#49](https://github.com/ome/ome-model/pull/49)
* CMake: use CMP0067 to enable standard setting in feature tests
  [#47](https://github.com/ome/ome-model/pull/47)
* CMake: remove REQUIRED from exported configuration
  [#54](https://github.com/ome/ome-model/pull/54)
* CMake: remove find modules distributed with CMake
  [#59](https://github.com/ome/ome-model/pull/59)

Documentation updates:

* Update OME website URLs and copyright years
  [#48](https://github.com/ome/ome-model/pull/48)
* Add versioning note and update README
  [#50](https://github.com/ome/ome-model/pull/50)
* Add OMERO pyramid specification to the documentation
  [#55](https://github.com/ome/ome-model/pull/55)
* Fix miscellaneous links [#56](https://github.com/ome/ome-model/pull/56)
  [#57](https://github.com/ome/ome-model/pull/57)
  [#58](https://github.com/ome/ome-model/pull/58)
  [#60](https://github.com/ome/ome-model/pull/60)

5.5.7 (2017-07-11)
------------------

* CMake: move options inclusion after project call
  [#42](https://github.com/ome/ome-model/pull/42)

Documentation updates:

* Use new OME Sphinx theme [#44](https://github.com/ome/ome-model/pull/44)

5.5.6 (2017-06-15)
------------------

* xsd-fu: correct C++ model object template
  [#41](https://github.com/ome/ome-model/pull/41)

Documentation updates:

* Use master as the source branch
  [#40](https://github.com/ome/ome-model/pull/40)

5.5.5 (2017-06-15)
------------------

Released as 5.5.6

5.5.4 (2017-06-09)
------------------

* Update OME-XML API reference including use of deleted methods
  [#38](https://github.com/ome/ome-model/pull/38)
* CMake: use C++ standard variable as documented
  [#39](https://github.com/ome/ome-model/pull/39)

5.5.3 (2017-05-24)
------------------

* Increase OMECommon and OMECompat requirements
  [#37](https://github.com/ome/ome-model/pull/37)
* CMake: add support for Boost 1.64
  [#35](https://github.com/ome/ome-model/pull/35)

Documentation updates:

* Fix BigTIFF links [#34](https://github.com/ome/ome-model/pull/34)

5.5.2 (2017-02-28)
------------------

Documentation updates:

* Add documentation links to the README
  [#32](https://github.com/ome/ome-model/pull/32)
* Reorganize OME-TIFF samples [#31](https://github.com/ome/ome-model/pull/31)
* Add BBBC and MitoCheck datasets to the OME-TIFF samples page
  [#33](https://github.com/ome/ome-model/pull/33)

5.5.1 (2017-02-16)
------------------

* OME-XML C++: insert missing links [#30](https://github.com/ome/ome-model/pull/30)

5.5.0 (2017-02-10)
------------------

* Enable C++ 11 support [#10](https://github.com/ome/ome-model/pull/10)
* Add minimal C++ 11 features [#25](https://github.com/ome/ome-model/pull/25)
* OME-XML performance improvements
  [#28](https://github.com/ome/ome-model/pull/28)
* CMake: obtain release version from Maven
  [#29](https://github.com/ome/ome-model/pull/29)

5.4.0 (2017-01-05)
------------------

* Fix ROI transforms [#14](https://github.com/ome/ome-model/pull/14)
* Add transform example to ROI OME-XML sample
  [#13](https://github.com/ome/ome-model/pull/13)
* Cleanup POM files [#11](https://github.com/ome/ome-model/pull/11)
  [#15](https://github.com/ome/ome-model/pull/15)
  [#16](https://github.com/ome/ome-model/pull/16)
  [#18](https://github.com/ome/ome-model/pull/18)
* Support conversion checks for Java and C++
  [#12](https://github.com/ome/ome-model/pull/12)
* CMake: drop gtest source building support
  [#9](https://github.com/ome/ome-model/pull/9)
* CMake: add support for Boost 1.63
  [#21](https://github.com/ome/ome-model/pull/21)
* CMake: change project name to ome-model
  [#20](https://github.com/ome/ome-model/pull/20)


5.3.1 (2016-11-03)
------------------

* Use ome-common 5.3.1 [#7](https://github.com/ome/ome-model/pull/7)
* Fix schema publication scripts [#6](https://github.com/ome/ome-model/pull/6)

5.3.0 (2016-10-25)
------------------

* Decouple the `ome-model` component from the Bio-Formats source code
* Drop `xsd-fu` code-generation tool as a Java module
  [#2](https://github.com/ome/ome-model/pull/2)
* Add build support for Maven and CMake
  [#1](https://github.com/ome/ome-model/pull/1)
