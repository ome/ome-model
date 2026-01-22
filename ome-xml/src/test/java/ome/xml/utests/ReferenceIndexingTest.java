/*
 * #%L
 * OME XML library
 * %%
 * Copyright (C) 2006 - 2016 Open Microscopy Environment:
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
 * Tests for indexed reference handling in OMEXMLMetadataImpl.
 *
 * These tests verify that references can be appended sequentially and
 * replaced at specific indices without causing NullPointerException.
 */
public class ReferenceIndexingTest {

  private OMEXMLMetadataImpl meta;

  @BeforeMethod
  public void setUp() {
    meta = new OMEXMLMetadataImpl();
  }

  /**
   * Test sequential appending of ROI references to an Image.
   * This tests the fix for the NPE when calling linkROI(null).
   */
  @Test
  public void testAppendImageROIReferences() {
    // Set up Image and ROIs
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);

    // Append ROI references sequentially
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:1", 0, 1);
    meta.setImageROIRef("ROI:2", 0, 2);

    // Verify count
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify each reference
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));
  }

  /**
   * Test replacement of ROI references at specific indices.
   */
  @Test
  public void testReplaceImageROIReferences() {
    // Set up Image and ROIs
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);
    meta.setROIID("ROI:3", 3);

    // Append ROI references
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:1", 0, 1);
    meta.setImageROIRef("ROI:2", 0, 2);

    assertEquals(3, meta.getImageROIRefCount(0));

    // Replace middle reference
    meta.setImageROIRef("ROI:3", 0, 1);

    // Verify count unchanged
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify replacement
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:3", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));
  }

  /**
   * Test that references survive MetadataConverter conversion.
   */
  @Test
  public void testROIReferencesAfterConversion() {
    // Set up source metadata
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:1", 0, 1);

    assertEquals(2, meta.getImageROIRefCount(0));

    // Convert to new metadata store
    OMEXMLMetadataImpl out = new OMEXMLMetadataImpl();
    MetadataConverter.convertMetadata(meta, out);

    // Verify references survived conversion
    assertEquals(2, out.getImageROIRefCount(0));
    assertEquals("ROI:0", out.getImageROIRef(0, 0));
    assertEquals("ROI:1", out.getImageROIRef(0, 1));
  }

  /**
   * Test sequential appending of Annotation references to an Image.
   */
  @Test
  public void testAppendImageAnnotationReferences() {
    // Set up Image and Annotations
    meta.setImageID("Image:0", 0);
    meta.setCommentAnnotationID("Annotation:0", 0);
    meta.setCommentAnnotationID("Annotation:1", 1);
    meta.setCommentAnnotationID("Annotation:2", 2);

    // Append annotation references sequentially
    meta.setImageAnnotationRef("Annotation:0", 0, 0);
    meta.setImageAnnotationRef("Annotation:1", 0, 1);
    meta.setImageAnnotationRef("Annotation:2", 0, 2);

    // Verify count
    assertEquals(3, meta.getImageAnnotationRefCount(0));

    // Verify each reference
    assertEquals("Annotation:0", meta.getImageAnnotationRef(0, 0));
    assertEquals("Annotation:1", meta.getImageAnnotationRef(0, 1));
    assertEquals("Annotation:2", meta.getImageAnnotationRef(0, 2));
  }

  /**
   * Test replacement of Annotation references at specific indices.
   */
  @Test
  public void testReplaceImageAnnotationReferences() {
    // Set up Image and Annotations
    meta.setImageID("Image:0", 0);
    meta.setCommentAnnotationID("Annotation:0", 0);
    meta.setCommentAnnotationID("Annotation:1", 1);
    meta.setCommentAnnotationID("Annotation:2", 2);
    meta.setCommentAnnotationID("Annotation:3", 3);

    // Append annotation references
    meta.setImageAnnotationRef("Annotation:0", 0, 0);
    meta.setImageAnnotationRef("Annotation:1", 0, 1);
    meta.setImageAnnotationRef("Annotation:2", 0, 2);

    assertEquals(3, meta.getImageAnnotationRefCount(0));

    // Replace first reference
    meta.setImageAnnotationRef("Annotation:3", 0, 0);

    // Verify count unchanged
    assertEquals(3, meta.getImageAnnotationRefCount(0));

    // Verify replacement
    assertEquals("Annotation:3", meta.getImageAnnotationRef(0, 0));
    assertEquals("Annotation:1", meta.getImageAnnotationRef(0, 1));
    assertEquals("Annotation:2", meta.getImageAnnotationRef(0, 2));
  }

  /**
   * Test multiple images with ROI references.
   */
  @Test
  public void testMultipleImagesWithROIReferences() {
    // Set up multiple Images and ROIs
    meta.setImageID("Image:0", 0);
    meta.setImageID("Image:1", 1);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);

    // Add ROIs to first image
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:1", 0, 1);

    // Add ROIs to second image
    meta.setImageROIRef("ROI:1", 1, 0);
    meta.setImageROIRef("ROI:2", 1, 1);

    // Verify counts
    assertEquals(2, meta.getImageROIRefCount(0));
    assertEquals(2, meta.getImageROIRefCount(1));

    // Verify first image references
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));

    // Verify second image references
    assertEquals("ROI:1", meta.getImageROIRef(1, 0));
    assertEquals("ROI:2", meta.getImageROIRef(1, 1));
  }

  /**
   * Test append and replace in same sequence.
   */
  @Test
  public void testMixedAppendAndReplace() {
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);
    meta.setROIID("ROI:3", 3);

    // Append first two
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:1", 0, 1);
    assertEquals(2, meta.getImageROIRefCount(0));

    // Replace first
    meta.setImageROIRef("ROI:2", 0, 0);
    assertEquals(2, meta.getImageROIRefCount(0));

    // Append third
    meta.setImageROIRef("ROI:3", 0, 2);
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify final state
    assertEquals("ROI:2", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:3", meta.getImageROIRef(0, 2));
  }

  /**
   * Test adding ROI references starting with a positive offset
   */
  @Test
  public void testAppendImageROIRefOffset() {
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);
    meta.setROIID("ROI:3", 3);

    // Append first three starting with non-zero reference index
    meta.setImageROIRef("ROI:0", 0, 2);
    meta.setImageROIRef("ROI:1", 0, 3);
    meta.setImageROIRef("ROI:2", 0, 4);
    assertEquals(0, meta.getImageROIRefCount(0));

    // Resolve the deferred references
    meta.resolveReferences();
    assertEquals(3, meta.getImageROIRefCount(0));
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));

    // Replace first
    meta.setImageROIRef("ROI:3", 0, 0);
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify final state
    assertEquals("ROI:3", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));
  }

  /**
   * Test adding ROI references in reverse order
   */
  @Test
  public void testAppendImageROIRefReverseOrder() {
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);
    meta.setROIID("ROI:3", 3);

    // Append first three in reverse order
    meta.setImageROIRef("ROI:2", 0, 2);
    meta.setImageROIRef("ROI:1", 0, 1);
    meta.setImageROIRef("ROI:0", 0, 0);
    assertEquals(1, meta.getImageROIRefCount(0));
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    // Resolve the deferred references
    meta.resolveReferences();
    assertEquals(3, meta.getImageROIRefCount(0));
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:2", meta.getImageROIRef(0, 1));
    assertEquals("ROI:1", meta.getImageROIRef(0, 2));

    // Replace first
    meta.setImageROIRef("ROI:3", 0, 0);
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify final state
    assertEquals("ROI:3", meta.getImageROIRef(0, 0));
    assertEquals("ROI:2", meta.getImageROIRef(0, 1));
    assertEquals("ROI:1", meta.getImageROIRef(0, 2));
  }

  /**
   * Test adding ROI references in non-sequential order
   */
  @Test
  public void testAppendImageROIRefNonSequentialOrder() {
    meta.setImageID("Image:0", 0);
    meta.setROIID("ROI:0", 0);
    meta.setROIID("ROI:1", 1);
    meta.setROIID("ROI:2", 2);
    meta.setROIID("ROI:3", 3);

    // Append first three in non-sequential order
    meta.setImageROIRef("ROI:1", 0, 1);
    meta.setImageROIRef("ROI:0", 0, 0);
    meta.setImageROIRef("ROI:2", 0, 2);
    assertEquals(1, meta.getImageROIRefCount(0));
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    // Resolve the deferred references
    meta.resolveReferences();
    assertEquals(3, meta.getImageROIRefCount(0));
    assertEquals("ROI:0", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));

    // Replace first
    meta.setImageROIRef("ROI:3", 0, 0);
    assertEquals(3, meta.getImageROIRefCount(0));

    // Verify final state
    assertEquals("ROI:3", meta.getImageROIRef(0, 0));
    assertEquals("ROI:1", meta.getImageROIRef(0, 1));
    assertEquals("ROI:2", meta.getImageROIRef(0, 2));
  }

  @Test
  public void testAppendFolderFolderRef() {
    meta.setFolderID("Folder:0", 0);
    meta.setFolderID("Folder:1", 1);
    meta.setFolderID("Folder:2", 2);
    meta.setFolderFolderRef("Folder:0", 2, 0);
    meta.setFolderFolderRef("Folder:1", 2, 1);

    assertEquals(0, meta.getFolderRefCount(0));
    assertEquals(0, meta.getFolderRefCount(1));
    assertEquals(2, meta.getFolderRefCount(2));
    assertEquals("Folder:0", meta.getFolderFolderRef(2, 0));
    assertEquals("Folder:1", meta.getFolderFolderRef(2, 1));

    // Replace first folder reference
    meta.setFolderID("Folder:3", 3);
    meta.setFolderFolderRef("Folder:3", 2, 0);
    assertEquals("Folder:3", meta.getFolderFolderRef(2, 0));
    assertEquals("Folder:1", meta.getFolderFolderRef(2, 1));
  }

  /**
   * Test adding ROI references non sequentially
   */
  @Test
  public void testAppendFolderFolderRefDeferred() {
    meta.setFolderID("Folder:1", 0);
    meta.setFolderID("Folder:2", 1);
    meta.setFolderFolderRef("Folder:0", 1, 0);
    meta.setFolderFolderRef("Folder:1", 1, 1);
    meta.setFolderID("Folder:0", 2);

    // Folder:0 was undefined when calling setFolderFolderRef
    // so the reference settings should be deferred
    assertEquals(0, meta.getFolderRefCount(0));
    assertEquals(0, meta.getFolderRefCount(1));
    assertEquals(0, meta.getFolderRefCount(2));

    // Resolve the deferred references
    meta.resolveReferences();
    assertEquals(2, meta.getFolderRefCount(1));
    assertEquals("Folder:0", meta.getFolderFolderRef(1, 0));
    assertEquals("Folder:1", meta.getFolderFolderRef(1, 1));

    // Replace first folder reference
    meta.setFolderID("Folder:3", 3);
    meta.setFolderFolderRef("Folder:3", 1, 0);
    assertEquals("Folder:3", meta.getFolderFolderRef(1, 0));
    assertEquals("Folder:1", meta.getFolderFolderRef(1, 1));
  }
}
