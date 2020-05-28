keyword_model_solr = {
    "corename": "keyword_model",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

doc_storage_solr = {
    "corename": "documents",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

file_storage = {
    "path": "~/filestorage"
}
