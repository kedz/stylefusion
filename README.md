# stylefusion
Sentence fusion driven style control?

A reimplementation of the DiscoFuse sentence splitting rules.

# Install 

`python setup.py develop`

# Download the latest corenlp

```bash
wget http://nlp.stanford.edu/software/stanford-corenlp-latest.zip 
unzip stanford-corenlp-latest.zip
```

# Start corenlp server

`./scripts/start-corenlp.sh stanford-corenlp-*`

# Run demo

`python scripts/demo.py`

# TODO
 - verb phrase coordination
 - anaphora
 - inter-sentence discourse connectives
 - recursive application utils  
