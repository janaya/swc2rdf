#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-
#
# 
# Copyright (C) 2010 julia dot anaya at gmail dot com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# Author: Julia Anaya
# Email: julia dot anaya at gmail dot com
#
# FILE:
# file-name
#
# DESCRIPTION:
# Python script to convert DBLP conferences to data.semanticweb.org conferences
#
# TODO: 

from rdflib import Namespace, RDF
# Namespaces
#RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SWRC = Namespace("http://swrc.ontoware.org/ontology#")

RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
ICAL = Namespace("http://www.w3.org/2002/12/cal/ical#")
SWC = Namespace("http://data.semanticweb.org/ns/swc/ontology#")
SWRC_EXT = Namespace("http://www.cs.vu.nl/~mcaklein/onto/swrc_ext/2005/05#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
D2R = Namespace("http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/config.rdf#")
DC = Namespace("http://purl.org/dc/elements/1.1/")



# SPARQL prefixes
PREFIX = "PREFIX "
#DSW
PREFIX_RDF = PREFIX + "rdf:<" + str(RDF.RDFNS) + ">"
PREFIX_SKOS = PREFIX + "skos:<" + str(SKOS) + ">" 
PREFIX_FOAF = PREFIX + "foaf:<" + str(FOAF) + ">"
PREFIX_SWRC = PREFIX + "swrc:<" + str(SWRC) + ">" 

PREFIX_RDFS = PREFIX + "rdfs:<" + str(RDFS) + ">" 
PREFIX_OWL = PREFIX + "owl:<" + str(OWL) + ">"
PREFIX_ICAL = PREFIX + "ical:<" + str(ICAL) + ">"
PREFIX_SWC = PREFIX + "swc:<" + str(SWC) + ">" 
PREFIX_SWRC_EXT = PREFIX + "swrc_ext:<" + str(SWRC_EXT) + ">"
#DBLP
PREFIX_DCTERMS = PREFIX + "dcterms:<" + str(DCTERMS) + ">"
PREFIX_XSD = PREFIX + "xsd:<" + str(XSD) + ">"
PREFIX_D2R = PREFIX + "d2r:<" + str(D2R) + ">"
PREFIX_DC = PREFIX + "dc:<" + str(DC) + ">"
