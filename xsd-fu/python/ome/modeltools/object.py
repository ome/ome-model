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
from collections import OrderedDict
from xml.etree import ElementTree

from ome.modeltools import config, language
from ome.modeltools.entity import OMEModelEntity
from ome.modeltools.property import OMEModelProperty


class OMEModelObject(OMEModelEntity):
    """
    A single element of an OME data model.
    """

    def __init__(self, element, parent, model):
        self.model = model
        self.element = element
        self.parent = parent
        self.base = element.getBase()
        self.name = element.getName()
        self.type = element.getType()
        self.properties = OrderedDict()
        self.isAbstract = False
        self.isParentOrdered = False
        self.isChildOrdered = False
        self.isOrdered = False
        self.isUnique = False
        self.isImmutable = False
        self._isGlobal = False
        self.plural = None
        self.manyToMany = False
        self.isAbstractSubstitution = self.model.opts.lang.hasSubstitutionGroup(
            self.name
        )
        self.isConcreteSubstitution = self.model.opts.lang.hasSubstitutionGroup(
            self.base
        )
        self.topLevelName = element.getName()
        self.hasPrimitiveBase = False
        if self.isConcreteSubstitution:
            self.topLevelName = self.base
        try:
            try:
                root = ElementTree.fromstring(element.appinfo)
            except:
                logging.error('Exception while parsing %r' % element.appinfo)
                raise
            if root.find('abstract') is not None:
                self.isAbstract = True
            if root.find('unique') is not None:
                self.isUnique = True
            if root.find('immutable') is not None:
                self.isImmutable = True
            if root.find('global') is not None:
                self._isGlobal = True
            if root.find('parentordered') is not None:
                self.isParentOrdered = True
            if root.find('childordered') is not None:
                self.isChildOrdered = True
            if root.find('ordered') is not None:
                self.isOrdered = True
            self.plural = root.findtext('plural')
        except AttributeError:
            pass

    def addBaseAttribute(self, delegate, namespace):
        prop = OMEModelProperty.fromReference(delegate, self, self.model)
        prop.hasBaseAttribute = True
        self.hasPrimitiveBase = True
        prop.isBackReference = False
        prop.isAttribute = True
        self.properties[delegate.name] = prop

    def addAttribute(self, attribute):
        """
        Adds an OME XML Schema attribute to the object's data model.
        """
        name = attribute.getName()
        self.properties[name] = OMEModelProperty.fromAttribute(
            attribute, self, self.model
        )

    def addElement(self, element):
        """
        Adds an OME XML Schema element to the object's data model.
        """
        name = element.getName()
        self.properties[name] = OMEModelProperty.fromElement(element, self, self.model)

    def _get_isAnnotation(self):
        if self.name == 'Annotation':
            return True
        base = self
        while True:
            if base is None:
                return False
            if base.base == 'Annotation':
                return True
            base = self.model.getObjectByName(base.base)

    isAnnotation = property(
        _get_isAnnotation, doc="""Whether or not the model object is an Annotation."""
    )

    def _get_isReference(self):
        if self.base == 'Reference':
            return True
        typeObject = self.model.getObjectByName(self.type)
        return (
            typeObject is not None
            and typeObject.name != self.name
            and typeObject.isReference
        )

    isReference = property(
        _get_isReference, doc="""Whether or not the model object is a reference."""
    )

    def _get_isAnnotated(self):
        return any(v.name == 'AnnotationRef' for v in self.properties.values())

    isAnnotated = property(
        _get_isAnnotated, doc="""Whether or not the model object is annotated."""
    )

    def _get_isNamed(self):
        for v in self.properties.values():
            if v.name == 'Name' and not v.isUnique:
                return True
        return False

    isNamed = property(
        _get_isNamed, doc="""Whether or not the model object is named."""
    )

    def _get_isDescribed(self):
        return any(v.name == 'Description' for v in self.properties.values())

    isDescribed = property(
        _get_isDescribed, doc="""Whether or not the model object is described."""
    )

    def _get_modelBaseType(self):
        """
        The base type is Object or String (Java) or None or std::string (C++).
        """
        base = self.element.getBase()
        if self.model.opts.lang.hasBaseType(base):
            base = self.model.opts.lang.baseType(base)
        if base is None and self.element.attrs['type'] != self.name:
            base = self.element.attrs['type']
        if base is None:
            base = self.model.opts.lang.getDefaultModelBaseClass()
        return base

    modelBaseType = property(
        _get_modelBaseType, doc="""The model object's base class."""
    )

    def _get_namespace(self):
        return self.element.namespace

    namespace = property(
        _get_namespace, doc="""The root namespace of the model object."""
    )

    def _get_baseObjectProperties(self):
        properties = list()
        base = self.base
        while True:
            base = self.model.getObjectByName(base)
            if base is None:
                return properties
            properties += list(base.properties.values())
            base = base.base

    baseObjectProperties = property(
        _get_baseObjectProperties, doc="""The model object's base object properties."""
    )

    def _get_langType(self):
        return self.name

    langType = property(_get_langType, doc="""The model object's type.""")

    def _get_langTypeNS(self):
        return '%s%s%s' % (
            self.model.opts.lang.omexml_model_package,
            self.model.opts.lang.package_separator,
            self.langType,
        )

    langTypeNS = property(
        _get_langTypeNS, doc="""The model object's type with namespace."""
    )

    def _get_langBaseType(self):
        if self.model.opts.lang.hasType(self.base):
            return self.model.opts.lang.type(self.base)
        else:
            if self.base is not None:
                simpleType = self.model.getTopLevelSimpleType(self.base)
                parent = self.model.getObjectByName(self.base)
                if simpleType is not None:
                    return self.resolveLangTypeFromSimpleType(self.base)
                if parent is not None:
                    return parent.langBaseType
            return self.model.opts.lang.base_class

    langBaseType = property(_get_langBaseType, doc="The model object's base type.")

    def _get_langBaseTypeNS(self):
        name = self.langBaseType
        if isinstance(self.model.opts.lang, language.Java):
            name = 'ome.xml.model.%s' % self.langBaseType
        return name

    langBaseTypeNS = property(
        _get_langBaseTypeNS, doc="The model object's type with namespace."
    )

    def _get_instanceVariableName(self):
        name = None
        if self.isManyToMany:
            name = self.argumentName + 'Links'
        if name is None:
            try:
                if self.maxOccurs > 1:
                    name = self.lowerCasePrefix(self.plural)
            except AttributeError:
                pass
        if name is None:
            name = self.argumentName

        return name

    instanceVariableName = property(
        _get_instanceVariableName, doc="""The property's instance variable name."""
    )

    def _get_instanceVariables(self):
        props = list()

        if self.langBaseType != self.model.opts.lang.base_class:
            props.append(
                [self.langBaseType, 'value', None, "Element's text data", False]
            )
        props.extend(
            [
                prop.instanceVariableType,
                prop.instanceVariableName,
                prop.instanceVariableDefault,
                prop.instanceVariableComment,
                prop.isUnitsEnumeration,
            ]
            for prop in self.properties.values()
            if not prop.isUnitsEnumeration
        )
        return props

    instanceVariables = property(
        _get_instanceVariables, doc="""The instance variables of this class."""
    )

    def _get_header(self):
        header = None
        if self.name in list(self.model.opts.lang.model_type_map.keys()):
            pass
        elif isinstance(self.model.opts.lang, language.Java):
            header = 'ome.xml.model.%s' % self.name
        return header

    header = property(
        _get_header,
        doc="The model object's include/import name. "
        'Does not include dependent headers.',
    )

    def _get_source_deps(self):
        deps = set()

        if self.name in list(self.model.opts.lang.model_type_map.keys()):
            pass
        elif isinstance(self.model.opts.lang, language.Java):
            pass

        for prop in self.properties.values():
            deps.update(prop.source_dependencies)

        return sorted(deps)

    source_dependencies = property(
        _get_source_deps,
        doc="""The object's dependencies for include/import in sources.""",
    )

    def _get_parents(self):
        return self.model.resolve_parents(self.name)

    parents = property(_get_parents, doc="""The parents for this object.""")

    def _get_parent(self):
        parents = self.model.resolve_parents(self.name)

        parent = None

        if parents is not None:
            parent = self.model.getObjectByName(next(iter(parents.keys())))

        return parent

    def _get_parentName(self):
        parent = self._get_parent()
        name = self.modelBaseType

        if (
            parent is not None
            and parent.isAbstract
            and self.name not in config.ANNOTATION_OVERRIDE
        ):
            name = parent.name

        return name

    parentName = property(
        _get_parentName, doc="""The parent class name for this object."""
    )

    def _get_isParentAbstract(self):
        parent = self._get_parent()

        abstract = False

        if (
            parent is not None
            and parent.isAbstract
            and self.name not in config.ANNOTATION_OVERRIDE
        ):
            abstract = True

        return abstract

    isParentAbstract = property(
        _get_isParentAbstract,
        doc="""Returns whether or not the model object has an abstract"""
        """ parent.""",
    )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<"%s" OMEModelObject instance at 0x%x>' % (self.name, id(self))
