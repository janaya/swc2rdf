#!/bin/sh
# http://www.informatik.uni-trier.de/~ley/db/conf/swap/
for Y in 2004 2005 2006 2007 2008; do wget http://dblp.uni-trier.de/rec/bibtex/conf/swap/$Y.xml; done
for Y in 2004 2005 2006 2007 2008; do wget http://www.informatik.uni-trier.de/~ley/db/conf/swap/swap$Y.html; done
grep -ohE 'http\:\/\/dblp\.uni-trier\.de\/rec\/bibtex\/conf\/swap\/([a-zA-Z0-9 -\_]+)\.xml' swap20*.html  > xmlfiles
while read LINE; do wget $LINE; done < xmlfiles
for XML in *xml; do xsltproc -o $(basename $XML .xml).rdf ../dblp2rdf.xsl $XML; done
for RDF in *rdf; do 4s-import dblp $RDF; done

