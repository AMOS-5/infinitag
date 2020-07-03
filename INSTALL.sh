# install dependencies
pip3 install -r requirements.txt
python3 -c "import nltk; nltk.download('all')"
python3 -m spacy download de_core_news_sm

# pytest-solr depends on this name! (I know) so don't change it!
mkdir downloads
pushd downloads

# install tika
mkdir tika
wget -O tika/tika-server.jar http://search.maven.org/remotecontent?filepath=org/apache/tika/tika-server/1.24/tika-server-1.24.jar

# install solr
wget http://archive.apache.org/dist/lucene/solr/8.5.1/solr-8.5.1.tgz
tar xzf solr-8.5.1.tgz
rm solr-8.5.1.tgz

popd
