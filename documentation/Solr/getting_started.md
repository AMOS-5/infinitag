# Solr

## Installation

    https://lucene.apache.org/solr/guide/8_5/solr-tutorial.html

## Dependencies

    python 2.7 - 3.7

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
create a core ("table") and attach to running solr instance

    solr create_core -c <corename> <optional -p PORT>

## delete
delete a core entirely, the working directory will also be deleted

    solr delete -c <corename>

## visual overview
    localhost:8983/solr/#/<corename>

## create the tags core

contains utility for creating core automatically for tests etc.

    python backend/tagstorage_setup.py

## comment on pysolr

I had problems creating a core with the library, if you don't have problems, then it's something on my side. This fixed it for me:

    L:1307 change this
    resp = requests.get(url, data=safe_urlencode(params), headers=headers)

    to

    resp = requests.get(url, data=params, headers=headers)
