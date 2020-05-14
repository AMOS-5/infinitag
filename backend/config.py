tag_storage_solr = {
    # name of the field where the tag is stored
    "field": "tag",
    # name of the database
    "corename": "tags",
    "url": "http://ec2-52-205-45-244.compute-1.amazonaws.com:8983/solr/",
    "always_commit": True, # will instantly apply changes, maybe change later
    # later for deployment machine
    # "url": "localhost:8983/solr/",
}

doc_storage_solr = {
    "corename": "documents",
    "url": "http://ec2-52-205-45-244.compute-1.amazonaws.com:8983/solr/",
    "always_commit": True, # will instantly apply changes, maybe change later
    "debug": True, # prints pipe output
    # later for deployment machine
    # "url": "localhost:8983/solr/",
}

file_storage = {
    "path": "~/filestorage"
}
