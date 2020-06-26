# install dependencies
pip3 install -r requirements.txt
python3 -c "import nltk; nltk.download('all')"
python3 -m spacy download de_core_news_sm

# install tika
wget -O tika-server.jar http://search.maven.org/remotecontent?filepath=org/apache/tika/tika-server/1.24/tika-server-1.24.jar
