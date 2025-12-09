/*
 * #%L
 * OME XML library
 * %%
 * Copyright (C) 2006 - 2025 Open Microscopy Environment:
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

import static org.testng.AssertJUnit.*;

import ome.xml.meta.MetadataConverter;
import ome.xml.meta.OMEXMLMetadataImpl;

import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

/**
 */
public class ReferenceTest {

  public static final String IMAGE_ID = "Image:0";

  public static final String[] ROI_IDS = {"ROI:0", "ROI:1", "ROI:2"};

  private OMEXMLMetadataImpl metadata;

  @BeforeMethod
  public void setUp() {
    metadata = new OMEXMLMetadataImpl();
    metadata.setImageID(IMAGE_ID, 0);

    for (int i=0; i<ROI_IDS.length; i++) {
      metadata.setROIID(ROI_IDS[i], i);
    }
  }

  @Test
  public void checkResolvedReferences() {
    for (int i=0; i<ROI_IDS.length; i++) {
      metadata.setImageROIRef(ROI_IDS[i], 0, i);
    }
    metadata.resolveReferences();
    OMEXMLMetadataImpl converted = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(metadata, converted);
    converted.resolveReferences();

    assertEquals(converted.getImageROIRefCount(0), ROI_IDS.length);
    for (int i=0; i<ROI_IDS.length; i++) {
      assertEquals(converted.getImageROIRef(0, i), ROI_IDS[i]);
    }
  }

  @Test
  public void checkAutoReferenceResolution() {
    for (int i=0; i<ROI_IDS.length; i++) {
      metadata.setImageROIRef(ROI_IDS[i], 0, i);
    }
    OMEXMLMetadataImpl converted = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(metadata, converted);

    assertEquals(converted.getImageROIRefCount(0), ROI_IDS.length);
    for (int i=0; i<ROI_IDS.length; i++) {
      assertEquals(converted.getImageROIRef(0, i), ROI_IDS[i]);
    }
  }

  @Test
  public void checkUpdatedReference() {
    metadata.setImageROIRef(ROI_IDS[1], 0, 0);
    metadata.setImageROIRef(ROI_IDS[0], 0, 0);

    OMEXMLMetadataImpl converted = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(metadata, converted);
    assertEquals(converted.getImageROIRefCount(0), 1);
    assertEquals(converted.getImageROIRef(0, 0), ROI_IDS[0]);
  }

  @Test
  public void checkReferencesOutOfOrder() {
    for (int i=0; i<ROI_IDS.length; i++) {
      metadata.setImageROIRef(ROI_IDS[i], 0, ROI_IDS.length - i - 1);
    }
    OMEXMLMetadataImpl converted = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(metadata, converted);
    assertEquals(converted.getImageROIRefCount(0), ROI_IDS.length);
    for (int i=0; i<ROI_IDS.length; i++) {
      assertEquals(converted.getImageROIRef(0, ROI_IDS.length - i - 1), ROI_IDS[i]);
    }
  }

}
