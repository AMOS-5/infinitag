# Solr

## Installation

    https://lucene.apache.org/solr/guide/8_5/solr-tutorial.html

## Dependencies

    python 3.7

# Getting started

    export PATH=$PATH:<PATH_TO_SOLR>/bin/
    solr -help

## access the solr executeable
    linuxlike: solr start
    windows: solr.cmd start

    in the following solr is used as a synonym for solr.cmd

## start
will start a solr instance on port 8983

    solr start <optional -p PORT>

## stop
will stop all running solr instances

    solr stop

## create

    solr create_core -c <corename> <optional -p PORT>

## delete
delete a core entirely, the working directory will also be deleted

    solr delete -c <corename>

## visual overview
    localhost:8983/solr/#/<corename>
