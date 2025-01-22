# Copyright (C) 2009 - 2016 Open Microscopy Environment:
#   - Board of Regents of the University of Wisconsin-Madison
#   - Glencoe Software, Inc.
#   - University of Dundee
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging

from xml.etree import ElementTree

from ome.modeltools.entity import OMEModelEntity
from ome.modeltools import config
from ome.modeltools import language
from ome.modeltools.exceptions import ModelProcessingError


class OMEModelProperty(OMEModelEntity):
    """
    An aggregate type representing either an OME XML Schema element,
    attribute or our OME XML Schema "Reference" meta element (handled by the
    ReferenceDelegate class). This class equates conceptually to an object
    oriented language instance variable which may be of a singular type or a
    collection.
    """

    def __init__(self, delegate, parent, model):
        self.model = model
        self.delegate = delegate
        self.parent = parent
        self.isAttribute = False
        self.isBackReference = False
        self.isChoice = hasattr(self.delegate, 'choice')
        self.isChoice = self.isChoice and self.delegate.choice is not None
        self._isGlobal = False
        self.plural = None
        self.manyToMany = False
        self.isParentOrdered = False
        self.isChildOrdered = False
        self.isOrdered = False
        self.isUnique = False
        self.isImmutable = False
        self.isInjected = False
        self._isReference = False
        self.hasBaseAttribute = False
        self.enumProps = None
        self.enumDocs = None

        try:
            root = None
            try:
                root = ElementTree.fromstring(delegate.appinfo)
            except Exception:
                # Can occur if there's an error, or we're processing
                # garbage, which occurs when generateds mangles the
                # input for enums with appinfo per enum.
                logging.debug('Exception while parsing %r' % delegate.appinfo)
            if root is not None:
                self.plural = root.findtext('plural')
                if root.find('manytomany') is not None:
                    self.manyToMany = True
                if root.find('parentordered') is not None:
                    self.isParentOrdered = True
                if root.find('childordered') is not None:
                    self.isChildOrdered = True
                if root.find('ordered') is not None:
                    self.isOrdered = True
                if root.find('unique') is not None:
                    self.isUnique = True
                if root.find('immutable') is not None:
                    self.isImmutable = True
                if root.find('injected') is not None:
                    self.isInjected = True
                if root.find('global') is not None:
                    self._isGlobal = True
        except AttributeError:
            pass

    def _get_type(self):
        if self.isAttribute:
            return self.delegate.getData_type()
        return self.delegate.getType()
    type = property(_get_type, doc="""The property's XML Schema data type.""")

    def _get_maxOccurs(self):
        if self.isAttribute:
            return 1
        choiceMaxOccurs = 1
        if self.isChoice:
            choiceMaxOccurs = self.delegate.choice.getMaxOccurs()
        return max(choiceMaxOccurs, self.delegate.getMaxOccurs())
    maxOccurs = property(
        _get_maxOccurs,
        doc="""The maximum number of occurrences for this property.""")

    def _get_minOccurs(self):
        if self.isAttribute and (hasattr(self.delegate, 'use')):
            if self.delegate.getUse() == "optional":
                return 0
            return 1
        if (hasattr(self.delegate, 'choice') and
                self.delegate.choice is not None):
            return self.delegate.choice.getMinOccurs()
        return self.delegate.getMinOccurs()
    minOccurs = property(
        _get_minOccurs,
        doc="""The minimum number of occurrences for this property.""")

    def _get_name(self):
        return self.delegate.getName()
    name = property(_get_name, doc="""The property's name.""")

    def _get_namespace(self):
        if self.isReference:
            ref = self.model.getObjectByName(
                config.REF_REGEX.sub('', self.type))
            return ref.namespace
        if self.isAttribute or self.isBackReference:
            return self.parent.namespace
        return self.delegate.namespace
    namespace = property(
        _get_namespace, doc="""The root namespace of the property.""")

    def _get_instanceType(self):
        """
        Type for creating a real concrete instance of this specific
        element, without any additional type overrides.  Normally,
        this won't be needed.  Use only where it's essential not to
        have any implicit overrides substituted for the real type.
        """
        return self.name
    instanceType = property(
        _get_instanceType, doc="""The property's instance type.""")

    def _get_langType(self):
        name = None

        if self.hasUnitsCompanion:
            name = self.unitsType

        # Hand back the type of enumerations
        if self.isEnumeration:
            langType = self.name
            if len(self.delegate.values) == 0:
                # As we have no directly defined possible values we have
                # no reason to qualify our type explicitly.
                name = self.type
            elif langType == "Type":
                # One of the OME XML unspecific "Type" properties which
                # can only be qualified by the parent.
                if self.type.endswith("string"):
                    # We've been defined entirely inline, prefix our
                    # type name with the parent type's name.
                    name = "%s%s" % (self.parent.name, langType)
                else:
                    # There's another type which describes us, use its name
                    # as our type name.
                    name = self.type
            else:
                name = langType
            # Handle XML Schema types that directly map to language types and
            # handle cases where the type is prefixed by a namespace
            # definition. (ex. OME:NonNegativeInt).
        else:
            # This sets name only for those types mentioned in the type_map
            # for the generated language. All other cases set name to None
            # so the following if block is executed
            name = self.model.opts.lang.type(self.type.replace('OME:', ''))

        if name is None:
            # Hand back the type of references or complex types with the
            # useless OME XML 'Ref' suffix removed.
            if (self.isBackReference or
                    (not self.isAttribute and self.delegate.isComplex())):
                name = config.REF_REGEX.sub('', self.type)
            # Hand back the type of complex types
            elif not self.isAttribute and self.delegate.isComplex():
                name = self.type
            elif not self.isEnumeration:
                # We have a property whose type was defined by a top level
                # simpleType.
                simpleTypeName = self.type
                name = self.resolveLangTypeFromSimpleType(simpleTypeName)
            else:
                logging.debug("%s dump: %s" % (self, self.__dict__))
                logging.debug("%s delegate dump: %s"
                              % (self, self.delegate.__dict__))
                raise ModelProcessingError(
                    "Unable to find %s type for %s" % (self.name, self.type))
        return name
    langType = property(_get_langType, doc="""The property's type.""")

    def _get_langTypeNS(self):
        return self.langType
    langTypeNS = property(
        _get_langTypeNS, doc="""The property's type with namespace.""")

    def _get_metadataStoreArgType(self):
        mstype = None

        if self.hasUnitsCompanion:
            if isinstance(self.model.opts.lang, language.Java):
                mstype = self.model.opts.lang.typeToUnitsType(
                    self.unitsCompanion.metadataStoreArgType)

        if self.name == "Transform":
            if isinstance(self.model.opts.lang, language.Java):
                mstype = "AffineTransform"

        if isinstance(self.model.opts.lang, language.Java):
            if (mstype is None and not self.isPrimitive and
                    not self.isEnumeration):
                mstype = "String"
            if mstype is None:
                mstype = self.langType
        return mstype
    metadataStoreArgType = property(
        _get_metadataStoreArgType,
        doc="""The property's MetadataStore argument type.""")

    def _get_metadataStoreRetType(self):
        mstype = None

        if self.hasUnitsCompanion:
            if isinstance(self.model.opts.lang, language.Java):
                mstype = self.model.opts.lang.typeToUnitsType(
                    self.unitsCompanion.metadataStoreRetType)

        if self.name == "Transform":
            if isinstance(self.model.opts.lang, language.Java):
                mstype = "AffineTransform"

        if isinstance(self.model.opts.lang, language.Java):
            if (mstype is None and not self.isPrimitive and
                    not self.isEnumeration):
                mstype = "String"
            if mstype is None:
                mstype = self.langType
        return mstype
    metadataStoreRetType = property(
        _get_metadataStoreRetType,
        doc="""The property's MetadataStore return type.""")

    def _get_isAnnotation(self):
        if self.isReference:
            ref = config.REF_REGEX.sub('', self.type)
            ref = self.model.getObjectByName(ref)
            return ref.isAnnotation
        return False
    isAnnotation = property(
        _get_isAnnotation,
        doc="""Whether or not the property is an Annotation.""")

    def _get_isPrimitive(self):
        return self.model.opts.lang.hasPrimitiveType(self.langType)
    isPrimitive = property(
        _get_isPrimitive,
        doc="""Whether or not the property's language type is a primitive.""")

    def _get_isEnumeration(self):
        v = self.delegate.getValues()
        return v is not None and len(v) > 0
    isEnumeration = property(
        _get_isEnumeration,
        doc="""Whether or not the property is an enumeration.""")

    def _get_isUnitsEnumeration(self):
        return self.langType.startswith('Units')
    isUnitsEnumeration = property(
        _get_isUnitsEnumeration,
        doc="""Whether or not the property is a units enumeration.""")

    def _get_hasUnitsCompanion(self):
        return self.name + 'Unit' in self.parent.properties
    hasUnitsCompanion = property(
        _get_hasUnitsCompanion,
        doc="""Whether or not the property has a units companion.""")

    def _get_unitsCompanion(self):
        if self.hasUnitsCompanion:
            return self.parent.properties[self.name+"Unit"]
        return None
    unitsCompanion = property(
        _get_unitsCompanion,
        doc="""The property's units companion.""")

    def _get_unitsType(self):
        if self.hasUnitsCompanion:
            return self.unitsCompanion.langType
        return None
    unitsType = property(
        _get_unitsType,
        doc="""The property's units type.""")

    def _get_unitsDefault(self):
        if self.hasUnitsCompanion:
            return self.unitsCompanion.defaultXsdValue
        return None
    unitsDefault = property(
        _get_unitsDefault,
        doc="""The property's default unit.""")

    def _get_enumProperties(self):
        if self.isEnumeration:
            if self.enumProps is None:
                self.enumProps = dict()

                try:
                    root = self.model.schemas['ome']
                    enum = None
                    for e in root.findall("{http://www.w3.org/2001/XMLSchema}simpleType"):
                        if e.get('name') is not None and e.get('name') == self.langType:
                            enum = e
                            break
                    if enum is None:
                        for e in root.findall(".//{http://www.w3.org/2001/XMLSchema}attribute"):
                            if e.get('name') is not None and e.get('name') == self.langType:
                                e2 = e.find('{http://www.w3.org/2001/XMLSchema}simpleType')
                                if e2 is not None:
                                    enum = e2
                                    break
                    for value in enum.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration"):
                        symbol = value.attrib['value']
                        props = value.find(".//xsdfu/enum")
                        if isinstance(self.model.opts.lang, language.Java) and getattr(props.attrib, 'javaenum', None) is not None:
                            props.attrib.enum = props.attrib.javaenum
                        self.enumProps[symbol] = props.attrib
                except AttributeError:
                    pass
        return self.enumProps
    enumProperties = property(
        _get_enumProperties,
        doc="""The property's enumeration properties.""")

    def _get_enumDocumentation(self):
        if self.isEnumeration:
            if self.enumDocs is None:
                self.enumDocs = dict()

                try:
                    root = self.model.schemas['ome']
                    for e in root.findall("{http://www.w3.org/2001/XMLSchema}simpleType"):
                        if e.get('name') is not None and e.get('name') == self.langType:
                            for e2 in e.findall('.//{http://www.w3.org/2001/XMLSchema}enumeration'):
                                symbol = e2.attrib['value']
                                doc = e2.find(".//{http://www.w3.org/2001/XMLSchema}documentation")
                                self.enumDocs[symbol] = doc.text
                except AttributeError:
                    pass

        return self.enumDocs
    enumDocumentation = property(
        _get_enumDocumentation,
        doc="""The property's enumeration documentation.""")

    def _get_isReference(self):
        o = self.model.getObjectByName(self.type)
        if o is not None:
            return o.isReference
        return self._isReference
    isReference = property(
        _get_isReference,
        doc="""Whether or not the property is a reference.""")

    def _get_concreteClasses(self):
        returnList = []
        if self.model.opts.lang.hasSubstitutionGroup(self.name):
            for o in sorted(self.model.objects.values(), key=lambda x: x.name):
                if o.parentName == self.name:
                    returnList.append(o.name)
        return returnList
    concreteClasses = property(
        _get_concreteClasses,
        doc="""Concrete instance types for an abstract type.""")

    def _get_possibleValues(self):
        return self.delegate.getValues()
    possibleValues = property(
        _get_possibleValues,
        doc="""If the property is an enumeration, its possible values.""")

    def _get_defaultValue(self):
        if "OTHER" in self.delegate.getValues():
            return "OTHER"
        else:
            return self.delegate.getValues()[0]
    defaultValue = property(
        _get_defaultValue,
        doc="""If the property is an enumeration, its default value.""")

    def _get_defaultXsdValue(self):
        return self.delegate.getDefault()
    defaultXsdValue = property(
        _get_defaultXsdValue,
        doc="""The default value, if any, that is set on the attribute.""")

    def _get_instanceVariableName(self):
        finalName = None
        name = self.argumentName
        if self.isManyToMany:
            if self.isBackReference:
                name = self.model.getObjectByName(self.type)
                name = name.instanceVariableName
                name = config.BACK_REFERENCE_NAME_OVERRIDE.get(self.key, name)
            finalName = name + 'Links'
        if finalName is None:
            try:
                if self.maxOccurs > 1:
                    plural = self.plural
                    if plural is None:
                        plural = self.model.getObjectByName(
                            self.methodName).plural
                        return self.lowerCasePrefix(plural)
            except AttributeError:
                pass
            if self.isBackReference:
                name = config.BACKREF_REGEX.sub('', name)
            finalName = name

        return finalName
    instanceVariableName = property(
        _get_instanceVariableName,
        doc="""The property's instance variable name.""")

    def _get_instanceVariableType(self):
        itype = None

        if isinstance(self.model.opts.lang, language.Java):
            if self.hasUnitsCompanion:
                itype = self.model.opts.lang.typeToUnitsType(
                    self.unitsCompanion.instanceVariableType)
            elif self.isReference and self.maxOccurs > 1:
                itype = "List<%s>" % self.langTypeNS
            elif self.isBackReference and self.maxOccurs > 1:
                itype = "List<%s>" % self.langTypeNS
            elif self.isBackReference:
                itype = self.langTypeNS
            elif self.maxOccurs == 1 and (
                    not self.parent.isAbstract or
                    self.isAttribute or not self.isComplex() or
                    not self.isChoice):
                itype = self.langTypeNS
            elif self.maxOccurs > 1 and not self.parent.isAbstract:
                itype = "List<%s>" % self.langTypeNS

        return itype
    instanceVariableType = property(
        _get_instanceVariableType,
        doc="""The property's Java instance variable type.""")

    def _get_instanceVariableDefault(self):
        idefault = None

        if isinstance(self.model.opts.lang, language.Java):
            if self.isReference and self.maxOccurs > 1:
                idefault = "ReferenceList<>"
            elif self.isBackReference and self.maxOccurs > 1:
                idefault = "ReferenceList<>"
            elif self.isBackReference:
                idefault = None
            elif self.maxOccurs == 1 and (
                    not self.parent.isAbstract or
                    self.isAttribute or not self.isComplex() or
                    not self.isChoice):
                idefault = None
            elif self.maxOccurs > 1 and not self.parent.isAbstract:
                idefault = "ArrayList<>"

        return idefault
    instanceVariableDefault = property(
        _get_instanceVariableDefault,
        doc="""The property's Java instance variable type.""")

    def _get_instanceVariableComment(self):
        icomment = ("*** WARNING *** Unhandled or skipped property %s"
                    % self.name)

        if self.isReference and self.maxOccurs > 1:
            icomment = "%s reference (occurs more than once)" % self.name
        elif self.isReference:
            icomment = "%s reference" % self.name
        elif self.isBackReference and self.maxOccurs > 1:
            icomment = "%s back reference (occurs more than once)" % self.name
        elif self.isBackReference:
            icomment = "%s back reference" % self.name
        elif self.maxOccurs == 1 and (
                not self.parent.isAbstract or self.isAttribute or
                not self.isComplex() or not self.isChoice):
            icomment = "%s property" % self.name
        elif self.maxOccurs > 1 and not self.parent.isAbstract:
            icomment = "%s property (occurs more than once)" % self.name

        return icomment

    instanceVariableComment = property(
        _get_instanceVariableComment,
        doc="""The property's Java instance variable comment.""")

    def _get_header(self):
        header = None
        if self.name in list(self.model.opts.lang.model_type_map.keys()) and self.name not in list(self.model.opts.lang.primitive_type_map.keys()):
            pass
        elif self.langType is None:
            pass
        elif isinstance(self.model.opts.lang, language.Java):
            if not self.model.opts.lang.hasPrimitiveType(self.langType):
                if self.isEnumeration:
                    header = "ome.xml.model.%s" % self.langType
                else:
                    header = "ome.xml.model.enums.%s" % self.langType
        return header
    header = property(
        _get_header,
        doc="The property's include/import name."
        " Does not include dependent headers.")

    def _get_source_deps(self):
        deps = set()
        if self.name in list(self.model.opts.lang.model_type_map.keys()):
            pass
        elif self.langType is None:
            pass
        elif isinstance(self.model.opts.lang, language.Java):
            if not self.model.opts.lang.hasPrimitiveType(self.langType):
                if self.isEnumeration:
                    deps.add("ome.xml.model.%s" % self.langType)
                else:
                    deps.add("ome.xml.model.enums.%s" % self.langType)

        return deps
    source_dependencies = property(
        _get_source_deps,
        doc="""The property's dependencies for include/import in sources.""")

    def isComplex(self):
        """
        Returns whether or not the property has a "complex" content type.
        """
        if self.isAttribute:
            raise ModelProcessingError(
                "This property is an attribute and has no content model!")
        # FIXME: This hack is in place because of the incorrect content
        # model in the XML Schema document itself for the "Description"
        # element.
        if self.name == "Description":
            return False
        if self.hasBaseAttribute:
            return False
        return self.delegate.isComplex()

    def _get_isAbstract(self):
        o = self.model.getObjectByName(self.name)
        if o is None:
            return False
        return o.isAbstract
    isAbstract = property(
        _get_isAbstract,
        doc="""Is the property abstract.""")

    def _get_isAbstractSubstitution(self):
        return self.model.opts.lang.hasSubstitutionGroup(self.name)
    isAbstractSubstitution = property(
        _get_isAbstract,
        doc="""Is the property an abstract type using substitution groups.""")

    def fromAttribute(klass, attribute, parent, model):
        """
        Instantiates a property from an XML Schema attribute.
        """
        instance = klass(attribute, parent, model)
        instance.isAttribute = True
        return instance
    fromAttribute = classmethod(fromAttribute)

    def fromElement(klass, element, parent, model):
        """
        Instantiates a property from an XML Schema element.
        """
        return klass(element, parent, model)
    fromElement = classmethod(fromElement)

    def fromReference(klass, reference, parent, model):
        """
        Instantiates a property from a "virtual" OME XML schema reference.
        """
        instance = klass(reference, parent, model)
        instance.isBackReference = True
        return instance
    fromReference = classmethod(fromReference)
