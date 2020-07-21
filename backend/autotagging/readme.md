## data_preprocessing.py

*    _Cleans Text From:_
     Punctuation,
     digits,
     un necessary words in the dictionary,
     Stop Words (using the english and german stopwords list by nltk),
     Lemmatize, 
     Tokenize and Split
     
*   Loads Files for tagging 

## K_means_cluster.py

* checks for optimal no. of clusters using Silhoutte method 

* Creates Kmeans cluters using Mini batch Kmeans and TF-IDF vectors

## Lda_model.py

* Does the topic modelling using LDA model from gensim 

## tf_idf_vector.py

* Creates the tags individually for the selected documents if it they are not eligible to be in a cluster

* Creates tf-idf vector and calculates distance using cosine similarity for kmeans clustering 

## tagcloud.py

* Creates the wordcloud or tag cloud for keywords availaible in the database.






