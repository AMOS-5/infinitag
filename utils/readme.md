## pre_processing.py

*    _Cleans Text From:_
     Punctuation,
     Stop Words (currently using the english stopwords list by nltk),
     Lemmatize, 
     Tokenize and Split

All the text files stored in the local directory (one folder) and applies the LDA model on top of it


## Requirements
 - pip install nltk
 - pip install gensim
 
 
## Run
 - python main.py directory\foldername



**Note:**
 -  Using the dummy data /i2b2- open source (healthcare) in a local directory for now
 -  Can be extended for german and other languages later
