CORENLP_PATH=$1
java  -Djava.io.tmpdir=`pwd` -Xmx4g -cp "$CORENLP_PATH/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
