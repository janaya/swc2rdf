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

try:
    from SPARQLWrapper import SPARQLWrapper, JSON
    from SPARQLWrapper.SPARQLExceptions import QueryBadFormed
except ImportError:
    sys.stderr.write("SPARQLWrapper must be installed")
    sys.exit(1)
import calendar
from conf import *
from namespaces import *
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)

PREFIXES_DBLP = PREFIX_FOAF + PREFIX_SWRC + PREFIX_RDF + PREFIX_RDFS \
        + PREFIX_OWL + PREFIX_DC + PREFIX_DCTERMS + PREFIX_XSD + PREFIX_D2R


def query(querystring, service):
    queryResults = []
    try:
        sparql = SPARQLWrapper(service)
        sparql.setQuery(querystring)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        if results.has_key("results"):
            results = results["results"]["bindings"]
            for result in results:
                if (len(result.keys()) == 1):
                    queryResults.append(result[result.keys()[0]]['value'])
                else:
                    one = {}
                    for key in result.keys():
                        one[key] = result[key]['value']
                    queryResults.append(one)
    except Exception, e:
        print "Exception calling query" #FIXME
        print e
    return queryResults


#    dblp_label, dblp_name, dblp_acron, dblp_city, \
#            dblp_country, dblp_month = get_dblp_data(dblp_url)

def dblp_conf_exists(uri):
    """
    SELECT DISTINCT *
    WHERE {
        <http://dblp.l3s.de/d2r/resource/publications/conf/swap/2010> ?p ?o.
    }
    """
    """
    SELECT DISTINCT *
    WHERE {
        <http://dblp.l3s.de/d2r/resource/conferences/swap> ?p ?o.
    }
    """
    """
    SELECT DISTINCT *
    WHERE {
        ?confseries rdfs:label "SWAP"^^xsd:string.
    }
    """
    """
    SELECT DISTINCT * WHERE {
      ?confseries rdfs:label "SWAP"^^xsd:string;
                  rdf:type swrc:Conference.
    }
    """
    """
    SELECT DISTINCT *
    WHERE {
        ?conf swrc:series <http://dblp.l3s.de/d2r/resource/conferences/swap> ; 
              a swrc:Proceedings;
              dcterms:issued ?year.
    }
    """

#PREFIX swrc: <http://swrc.ontoware.org/ontology#> PREFIX dcterms: <http://purl.org/dc/terms/> SELECT DISTINCT * WHERE { ?conf swrc:series <http://dblp.l3s.de/d2r/resource/conferences/swap> ; a swrc:Proceedings; dcterms:issued ?year. }

def get_dblp_uri(label, year):
    label = label.upper()
    query_get_dblp_uri = """
    SELECT DISTINCT *
    WHERE {
        ?confseries rdfs:label "%s"^^xsd:string;
                    dc:title "%s"^^xsd:string;
                    a swrc:Conference.
        ?conf swrc:series ?confseries;
              dcterms:issued "%s"^^xsd:gYear.
    }
    """
    t_query_get_dblp_uri = PREFIXES_DBLP + \
                                       query_get_dblp_uri
    dblp_uri = query(t_query_get_dblp_uri % (label, label, year), 
                            DBLP_SPARQL_ENDPOINT)
    return dblp_uri

def get_dblp_uri_year(label):
    label = label.upper()
#    query_get_dblp_uri_year = """
#    SELECT ?conf ?year
#    WHERE {
#        ?confseries rdfs:label "%s";
#                    dc:title "%s";
#                    a swrc:Conference;
#                    is swrc:series of ?conf.
#        ?conf a swrc:Proceedings;
#              a foaf:Document;  
#              swrc:series ?confseries;
#              dcterms:issued ?year.
#    }
#    """

#    query_get_dblp_uri_year = """
#    SELECT DISTINCT * WHERE {
#      ?confseries rdfs:label "SWAP"^^xsd:string;
#                  rdf:type swrc:Conference.
#      ?conf swrc:series ?confseries;
#            dcterms:issued ?year;
#            rdfs:label ?label;
#            rdf:type swrc:Proceedings;
#            rdf:type foaf:Document.
#    }
#    """

    query_get_dblp_uri_year = """
    SELECT DISTINCT * WHERE {
      ?confseries rdfs:label ?name;
                  rdf:type swrc:Conference.
      FILTER regex(?name, "%s", "i" ) 
    }
    """
    t_query_get_dblp_uri_year = PREFIXES_DBLP + \
                                       query_get_dblp_uri_year
    dblp_uri_year = query(t_query_get_dblp_uri_year % (label), 
                            DBLP_SPARQL_ENDPOINT)
    return dblp_uri_year



def get_dblp_year(confseries):
    query_get_dblp_year = """
    SELECT ?conf
    WHERE {
        ?conf swrc:series <http://dblp.l3s.de/d2r/page/resource/rr>; 
              a swrc:Proceedings;
              dcterms:issued ?year.
    }
    """
    t_query_get_dblp_year = PREFIXES_DBLP + \
                                       query_get_dblp_year
    dblp_year = query(t_query_get_dblp_year % confseries, 
                            DBLP_SPARQL_ENDPOINT)
    return dblp_year


def get_dblp_data(dblp_url):
    dblp_name = dblp_month = None
    query_get_label_from_dblp = """
    SELECT ?conflabel 
    WHERE {
        <%s> rdfs:label ?conflabel }
    """
    t_query_get_label_from_dblp = PREFIXES_DBLP + \
                                       query_get_label_from_dblp
    dblp_label = query(t_query_get_label_from_dblp % dblp_url, 
                            DBLP_SPARQL_ENDPOINT)
    if dblp_label:
#        dblp_name, dblp_acron, dblp_city, dblp_country, \
#        dblp_date, dblp_year = dblp_label[0].rsplit(".")[0].split(", ")
#        dblp_month = dblp_date.split()[0]
        dblp_name = dblp_label[0]
        for m in range(1,13):
            month = calendar.month_name[m]
            if dblp_name.find(month) > 0:
                print "month found: %s" % month
                dblp_month = month
#                label_list = label.split(month)
                break
    return dblp_name, dblp_month

def get_dblp_editors(dblp_url):
    query_get_editors_from_dblp = """
    SELECT ?uri ?name 
    WHERE {<%s> swrc:editor ?uri.
        ?uri foaf:name ?name.
      }
    """
    t_query_get_editors_from_dblp = PREFIXES_DBLP + \
                                        query_get_editors_from_dblp
    dblp_editors = query(t_query_get_editors_from_dblp % \
                              dblp_url, DBLP_SPARQL_ENDPOINT)
    return dblp_editors

def get_dblp_author_papers(dblp_url):
    query_get_authors_papers_from_dblp = """
    SELECT DISTINCT * WHERE {
        ?paper dcterms:partOf <%s>;
               rdfs:label ?paperlabel;
               foaf:maker ?author.
        ?author foaf:name ?authorname.
    }
    """
    t_query_get_authors_papers_from_dblp = PREFIXES_DBLP + \
    query_get_authors_papers_from_dblp

    dblp_authors_papers = query(
                                  t_query_get_authors_papers_from_dblp % \
                                  dblp_url, DBLP_SPARQL_ENDPOINT)
    logging.debug("Querying DBLP the papers and authors of conference %s" % dblp_uri)
    dblp_papers = {}
    dblp_authors = {}
    for i in dblp_authors_papers:
    #    if dblp_authors.get(i["authorname"], None):
    #        dblp_authors[i["authorname"]]['papers'].append(i["paper"])
    #    else:
    #        dblp_authors[i['authorname']] = {'authordblpuri':i['author'], 
    #                                'papers':[i['paper']]}
        if dblp_authors.get(i["author"], None):
            dblp_authors[i["author"]]['papers'].append(i["paper"])
        else:
            dblp_authors[i['author']] = {'name':i['authorname'], 
                                    'papers':[i['paper']]}
        if dblp_papers.get(i['paper'], None):
            dblp_papers[i['paper']]['authors'].append(i['author'])
        else:
            dblp_papers[i['paper']] = {'label':i['paperlabel'], 
                                  'authors':[i['author']]}
    return dblp_papers, dblp_authors
