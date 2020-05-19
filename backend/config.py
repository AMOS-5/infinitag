tag_storage_solr = {
    # name of the field where the tag is stored
    "field": "tag",
    # name of the database
    "corename": "tags",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

doc_storage_solr = {
    "corename": "documents",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
    "debug": True,  # prints pipe output
}

file_storage = {
    "path": "~/filestorage"
}
