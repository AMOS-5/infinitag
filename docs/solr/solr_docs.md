# Solr documentation

## Core overview

In the following we use `/bin/solr` as an abbrevation for `/your/path/to/solr/bin/solr`
Infinitag maintains several Solr cores. The configuration for the cores is in `config.py`.

All cores use the default configuration, except for the documents core.

Create all the needed cores for the app:

    default:
    /bin/solr create_core -c <corename>

    documents:
    /bin/solr create_core -c documents -d backend/solr/configs/documents_core

## Core dependencies

The `keyword_statistics core` depends on the CHANGING state of the `docs core` (keywords are added to statistics
when documents are updated in the `documents core`). So it is suggested to wipe both, if one has to be wiped. (see `cleardb.py`)

## Further reading

### Switch from managed-schema to schema.xml

    https://lucene.apache.org/solr/guide/6_6/schema-factory-definition-in-solrconfig.html#SchemaFactoryDefinitioninSolrConfig-SwitchingfromManagedSchematoManuallyEditedschema.xml

### How to enable data extraction from docx, ppt, pdf etc.

    https://lucene.apache.org/solr/guide/6_6/uploading-data-with-solr-cell-using-apache-tika.html#UploadingDatawithSolrCellusingApacheTika-ConfiguringtheSolrExtractingRequestHandler

    https://lucene.apache.org/solr/guide/8_5/uploading-data-with-solr-cell-using-apache-tika.html#configuring-the-extractingrequesthandler-in-solrconfig-xml
