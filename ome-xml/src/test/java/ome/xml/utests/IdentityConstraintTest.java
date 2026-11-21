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

import static org.testng.Assert.assertNotNull;
import static org.testng.Assert.assertTrue;
import static org.testng.Assert.fail;

import java.io.InputStream;
import java.net.URL;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;

import ome.specification.SchemaResolver;

import org.testng.annotations.BeforeClass;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;
import org.xml.sax.SAXException;

/**
 * Checks that the 2016-06 schema enforces its identity constraints.
 *
 * Each constraint has a pair of fixtures: the valid one must validate, and
 * the invalid one must be rejected by that constraint.
 */
public class IdentityConstraintTest {

  private static final String FIXTURES = "/identity-constraints/2016-06/";

  private Schema schema;

  @BeforeClass
  public void setUp() throws Exception {
    URL xsd = getClass().getResource("/released-schema/2016-06/ome.xsd");
    assertNotNull(xsd, "2016-06 schema not found on the classpath");
    SchemaFactory factory =
      SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
    factory.setResourceResolver(new SchemaResolver());
    schema = factory.newSchema(xsd);
  }

  @DataProvider(name = "constraints")
  public Object[][] constraints() {
    return new Object[][] {
      {"wellsampleindex", "WellSampleIndex"},
      {"image-roiref", "ImageROIIDKeyRef"},
      {"microbeam-manipulation-roiref",
       "ExperimentMicrobeamManipulationROIIDKeyRef"},
      {"laser-pump", "InstrumentLightSourceLaserPumpLightSourceIDKey"},
    };
  }

  @Test(dataProvider = "constraints")
  public void testValid(String fixture, String constraint) throws Exception {
    validate(fixture + "-valid.ome.xml");
  }

  @Test(dataProvider = "constraints")
  public void testInvalid(String fixture, String constraint)
    throws Exception
  {
    String name = fixture + "-invalid.ome.xml";
    try {
      validate(name);
    }
    catch (SAXException e) {
      assertTrue(e.getMessage().contains(constraint),
        name + ": expected a " + constraint + " violation, got: " +
        e.getMessage());
      return;
    }
    fail(name + " validated; expected " + constraint + " to reject it");
  }

  private void validate(String name) throws Exception {
    URL url = getClass().getResource(FIXTURES + name);
    assertNotNull(url, name + " not found on the classpath");
    try (InputStream in = url.openStream()) {
      schema.newValidator().validate(new StreamSource(in, url.toString()));
    }
  }

}
