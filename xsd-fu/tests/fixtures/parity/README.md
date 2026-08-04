# Generated-output parity fixtures

The SHA-256 manifests in this directory are the byte-for-byte output contract
for `xsd-fu`. Model and metadata output were produced from commit
`1957bd781d54ea4fde815912f27ee94b950beb2c`.

For the 2012-06, 2013-06, and 2015-01 schemas, the legacy aggregate metadata
command stopped after producing five interface files because it compared them
with the repository's newer `MetadataConverter`. The sixth file,
`OMEXMLMetadataImpl.java`, was captured from the separately successful
`omexml_metadata` command. The 2016-06 aggregate command produced all six
metadata files directly.

The manifests intentionally contain relative paths so that parity checks are
independent of the checkout and temporary-output locations.
