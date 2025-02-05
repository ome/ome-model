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

import copy
import os

from ome.modeltools.exceptions import ModelProcessingError

TYPE_SOURCE = 'source'


class Language:
    """
    Base class for output language.
    Updates the type maps with the model namespace.
    """

    def __init__(self, namespace, templatepath):
        self.modelNamespace = namespace
        self._templatepath = templatepath

        # Separator for package/namespace
        self.package_separator = None

        # The default base class for OME XML model objects.
        self.default_base_class = None

        # A global mapping from XSD Schema types and language types
        # that is used to inform and override type mappings for OME
        # Model properties which are comprised of XML Schema
        # attributes, elements and OME XML reference virtual types. It
        # is a superset of primitive_type_map.
        self.type_map = None

        self.fundamental_types = set()

        self.primitive_types = set()

        self.primitive_base_types = set()

        self.base_class = None

        self.template_map = {
            'ENUM': 'OMEXMLModelEnum.template',
            'ENUM_INCLUDEALL': 'OMEXMLModelAllEnums.template',
            'ENUM_HANDLER': 'OMEXMLModelEnumHandler.template',
            'QUANTITY': 'OMEXMLModelQuantity.template',
            'CLASS': 'OMEXMLModelObject.template',
            'METADATA_STORE': 'MetadataStore.template',
            'METADATA_RETRIEVE': 'MetadataRetrieve.template',
            'METADATA_AGGREGATE': 'AggregateMetadata.template',
            'OMEXML_METADATA': 'OMEXMLMetadataImpl.template',
            'DUMMY_METADATA': 'DummyMetadata.template',
            'FILTER_METADATA': 'FilterMetadata.template',
        }

        # A global type mapping from XSD Schema types to language
        # primitive base classes.
        self.primitive_type_map = {
            'PositiveInt': 'PositiveInteger',
            'NonNegativeInt': 'NonNegativeInteger',
            'PositiveLong': 'PositiveLong',
            'NonNegativeLong': 'NonNegativeLong',
            'PositiveFloat': 'PositiveFloat',
            'NonNegativeFloat': 'NonNegativeFloat',
            'PercentFraction': 'PercentFraction',
            'Color': 'Color',
            'Text': 'Text',
            namespace + 'dateTime': 'Timestamp',
        }

        # A global type mapping from XSD Schema substitution groups to language abstract classes
        self.abstract_type_map = dict()
        # A global type mapping from XSD Schema abstract classes to their equivalent substitution group
        self.substitutionGroup_map = dict()

        # A global type mapping from XSD Schema elements to language model
        # object classes.  This will cause source code generation to be
        # skipped for this type since it's implemented natively.
        self.model_type_map = {}

        # A global type mapping from XSD Schema types to base classes
        # that is used to override places in the model where we do not
        # wish subclassing to take place.
        self.base_type_map = {
            'UniversallyUniqueIdentifier': self.getDefaultModelBaseClass(),
            'base64Binary': self.getDefaultModelBaseClass(),
        }

        # A global set XSD Schema types use as base classes which are primitive
        self.primitive_base_types = {'base64Binary'}

        self.model_unit_map = {}
        self.model_unit_default = {}

        self.name = None
        self.template_dir = None
        self.source_suffix = None
        self.converter_dir = None
        self.converter_name = None

        self.omexml_model_package = None
        self.omexml_model_enums_package = None
        self.omexml_model_quantity_package = None
        self.omexml_model_omexml_model_enum_handlers_package = None
        self.metadata_package = None
        self.omexml_metadata_package = None

    def _initTypeMap(self):
        self.type_map['Leader'] = 'Experimenter'
        self.type_map['Contact'] = 'Experimenter'
        self.type_map['Pump'] = 'LightSource'

    def getDefaultModelBaseClass(self):
        return None

    def getTemplate(self, name):
        return self.template_map[name]

    def getTemplateDirectory(self):
        return self.template_dir

    def templatepath(self, template):
        return os.path.join(
            self._templatepath, self.getTemplateDirectory(), self.getTemplate(template)
        )

    def getConverterDir(self):
        return self.converter_dir

    def getConverterName(self):
        return self.converter_name

    def generatedFilename(self, name, type):
        gen_name = None
        if type == TYPE_SOURCE and self.source_suffix is not None:
            gen_name = name + self.source_suffix
        else:
            raise ModelProcessingError(
                'Invalid language/filetype combination: %s/%s' % (self.name, type)
            )
        return gen_name

    def hasBaseType(self, type):
        return type in self.base_type_map

    def baseType(self, type):
        try:
            return self.base_type_map[type]
        except KeyError:
            return None

    def hasFundamentalType(self, type):
        return type in self.fundamental_types

    def hasPrimitiveType(self, type):
        return (
            type in list(self.primitive_type_map.values())
            or type in self.primitive_types
        )

    def primitiveType(self, type):
        try:
            return self.primitive_type_map[type]
        except KeyError:
            return None

    def hasAbstractType(self, type):
        return type in self.abstract_type_map

    def abstractType(self, type):
        try:
            return self.abstract_type_map[type]
        except KeyError:
            return None

    def hasSubstitutionGroup(self, type):
        return type in self.substitutionGroup_map

    def substitutionGroup(self, type):
        try:
            return self.substitutionGroup_map[type]
        except KeyError:
            return None

    def getSubstitutionTypes(self):
        return list(self.substitutionGroup_map.keys())

    def isPrimitiveBase(self, type):
        return type in self.primitive_base_types

    def hasType(self, type):
        return type in self.type_map

    def type(self, type):
        try:
            return self.type_map[type]
        except KeyError:
            return None

    def index_signature(self, name, max_occurs, level, dummy=False):
        sig = {
            'type': name,
        }

        if name[:2].isupper():
            sig['argname'] = '%sIndex' % name
        else:
            sig['argname'] = '%s%sIndex' % (name[:1].lower(), name[1:])

        return sig

    def index_string(self, signature, dummy=False):
        if dummy is False:
            return '%s %s' % (signature['argtype'], signature['argname'])
        else:
            return '%s /* %s */' % (signature['argtype'], signature['argname'])

    def index_argname(self, signature, dummy=False):
        return signature['argname']


class Java(Language):
    def __init__(self, namespace, templatepath):
        super().__init__(namespace, templatepath)

        self.package_separator = '.'

        self.base_class = 'Object'

        self.primitive_type_map[namespace + 'boolean'] = 'Boolean'
        self.primitive_type_map[namespace + 'string'] = 'String'
        self.primitive_type_map[namespace + 'integer'] = 'Integer'
        self.primitive_type_map[namespace + 'int'] = 'Integer'
        self.primitive_type_map[namespace + 'long'] = 'Long'
        self.primitive_type_map[namespace + 'float'] = 'Double'
        self.primitive_type_map[namespace + 'double'] = 'Double'
        self.primitive_type_map[namespace + 'anyURI'] = 'String'
        self.primitive_type_map[namespace + 'hexBinary'] = 'String'
        self.primitive_type_map['base64Binary'] = 'byte[]'
        self.primitive_type_map['Map'] = 'List<MapPair>'

        self.model_type_map['Map'] = None
        self.model_type_map['M'] = None
        self.model_type_map['K'] = None
        self.model_type_map['V'] = None

        self.model_unit_map['UnitsLength'] = 'Length'
        self.model_unit_map['UnitsPressure'] = 'Pressure'
        self.model_unit_map['UnitsAngle'] = 'Angle'
        self.model_unit_map['UnitsTemperature'] = 'Temperature'
        self.model_unit_map['UnitsElectricPotential'] = 'ElectricPotential'
        self.model_unit_map['UnitsPower'] = 'Power'
        self.model_unit_map['UnitsFrequency'] = 'Frequency'

        self.model_unit_default['UnitsLength'] = 'UNITS.METRE'
        self.model_unit_default['UnitsTime'] = 'UNITS.SECOND'
        self.model_unit_default['UnitsPressure'] = 'UNITS.PASCAL'
        self.model_unit_default['UnitsAngle'] = 'UNITS.RADIAN'
        self.model_unit_default['UnitsTemperature'] = 'UNITS.KELVIN'
        self.model_unit_default['UnitsElectricPotential'] = 'UNITS.VOLT'
        self.model_unit_default['UnitsPower'] = 'UNITS.WATT'
        self.model_unit_default['UnitsFrequency'] = 'UNITS.HERTZ'

        self.type_map = copy.deepcopy(self.primitive_type_map)
        self._initTypeMap()
        self.type_map['MIMEtype'] = 'String'

        self.name = 'Java'
        self.template_dir = 'templates/java'
        self.source_suffix = '.java'
        self.converter_name = 'MetadataConverter'
        self.converter_dir = 'ome-xml/src/main/java/ome/xml/meta'

        self.omexml_model_package = 'ome.xml.model'
        self.omexml_model_enums_package = 'ome.xml.model.enums'
        self.omexml_model_omexml_model_enum_handlers_package = (
            'ome.xml.model.enums.handlers'
        )
        self.metadata_package = 'ome.xml.meta'
        self.omexml_metadata_package = 'ome.xml.meta'

        self.units_implementation_is = 'ome'
        self.units_package = 'ome.units'
        self.units_implementation_imports = (
            'import ome.units.quantity.*;\nimport ome.units.*;'
        )
        self.model_unit_map['UnitsTime'] = 'Time'

    def getDefaultModelBaseClass(self):
        return 'AbstractOMEModelObject'

    def typeToUnitsType(self, unitType):
        return self.model_unit_map[unitType]

    def typeToDefault(self, unitType):
        return self.model_unit_default[unitType]

    def index_signature(self, name, max_occurs, level, dummy=False):
        """Makes a Java method signature dictionary from an index name."""

        sig = super().index_signature(name, max_occurs, level, dummy)
        sig['argtype'] = 'int'

        return sig


def create(language, namespace, templatepath):
    """
    Create a language by name.
    """

    lang = None

    if language == 'Java':
        lang = Java(namespace, templatepath)
    else:
        raise ModelProcessingError('Invalid language: %s' % language)

    return lang
