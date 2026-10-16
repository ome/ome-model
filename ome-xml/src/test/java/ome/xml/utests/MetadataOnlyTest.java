/*
 * #%L
 * OME XML library
 * %%
 * Copyright (C) 2006 - 2026 Open Microscopy Environment:
 *   - Massachusetts Institute of Technology
 *   - National Institutes of Health
 *   - University of Dundee
 *   - Board of Regents of the University of Wisconsin-Madison
 *   - Glencoe Software, Inc.
 * %%
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * #L%
 */

package ome.xml.utests;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertFalse;
import static org.testng.Assert.assertNull;
import static org.testng.Assert.assertTrue;

import java.io.StringReader;
import java.net.URL;
import java.util.Arrays;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.SchemaFactory;

import ome.xml.meta.AggregateMetadata;
import ome.xml.meta.BaseMetadata;
import ome.xml.meta.DummyMetadata;
import ome.xml.meta.FilterMetadata;
import ome.xml.meta.MetadataConverter;
import ome.xml.meta.OMEXMLMetadataImpl;
import ome.xml.model.enums.DimensionOrder;
import ome.xml.model.enums.PixelType;
import ome.xml.model.primitives.PositiveInteger;

import org.testng.annotations.Test;

/** Tests for MetadataOnly marker access and conversion. */
public class MetadataOnlyTest {

  @Test
  public void testMarkerPresence() {
    OMEXMLMetadataImpl metadata = createMetadata();

    assertFalse(metadata.getPixelsMetadataOnly(0));
    metadata.setPixelsMetadataOnly(true, 0);
    assertTrue(metadata.getPixelsMetadataOnly(0));
    assertTrue(metadata.dumpXML().contains("<MetadataOnly"));

    metadata.setPixelsMetadataOnly(false, 0);
    assertFalse(metadata.getPixelsMetadataOnly(0));
    assertFalse(metadata.dumpXML().contains("<MetadataOnly"));

    metadata.setPixelsMetadataOnly(null, 0);
    assertFalse(metadata.getPixelsMetadataOnly(0));
  }

  @Test
  public void testMarkerConversion() throws Exception {
    OMEXMLMetadataImpl source = createMetadata();
    source.setPixelsMetadataOnly(true, 0);

    OMEXMLMetadataImpl destination = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(source, destination);

    assertTrue(destination.getPixelsMetadataOnly(0));
    String xml = destination.dumpXML();
    assertTrue(xml.contains("<MetadataOnly"));
    URL schema = getClass().getResource("/released-schema/2016-06/ome.xsd");
    SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI)
      .newSchema(schema).newValidator()
      .validate(new StreamSource(new StringReader(xml)));
  }

  @Test
  public void testMetadataWrappers() {
    DummyMetadata unsupported = new DummyMetadata();
    assertNull(unsupported.getPixelsMetadataOnly(0));
    unsupported.setPixelsMetadataOnly(true, 0);

    OMEXMLMetadataImpl source = createMetadata();
    source.setPixelsMetadataOnly(true, 0);
    AggregateMetadata aggregate = new AggregateMetadata(
      Arrays.<BaseMetadata>asList(unsupported, source));
    assertEquals(aggregate.getPixelsMetadataOnly(0), Boolean.TRUE);

    OMEXMLMetadataImpl destination = new OMEXMLMetadataImpl();
    FilterMetadata filter = new FilterMetadata(destination, true);
    filter.setPixelsMetadataOnly(true, 0);
    assertTrue(destination.getPixelsMetadataOnly(0));
  }

  private OMEXMLMetadataImpl createMetadata() {
    OMEXMLMetadataImpl metadata = new OMEXMLMetadataImpl();
    PositiveInteger one = new PositiveInteger(1);
    metadata.setImageID("Image:0", 0);
    metadata.setPixelsID("Pixels:0", 0);
    metadata.setPixelsDimensionOrder(DimensionOrder.XYZCT, 0);
    metadata.setPixelsType(PixelType.UINT8, 0);
    metadata.setPixelsSizeX(one, 0);
    metadata.setPixelsSizeY(one, 0);
    metadata.setPixelsSizeZ(one, 0);
    metadata.setPixelsSizeC(one, 0);
    metadata.setPixelsSizeT(one, 0);
    return metadata;
  }
}
