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

from conf import *
from namespaces import *

PREFIXES_DSW = PREFIX_FOAF + PREFIX_SWRC


def query(query, service):
    queryResults = []
    try:
        sparql = SPARQLWrapper(service)
        sparql.setQuery(query)
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

def get_mbox_homepage_from_name(name):
    query_mbox_homepage_from_name = """
    SELECT DISTINCT ?personuri ?mbox_sha1sum ?homepage
    WHERE { 
        ?personuri a foaf:Person.
        OPTIONAL {?personuri foaf:name ?name}. 
        OPTIONAL {?personuri foaf:mbox_sha1sum ?mbox_sha1sum}.
        OPTIONAL {?personuri foaf:homepage ?homepage}.
        FILTER regex(?name, "%s", "i" ) 
    }
    """
    t_query_mbox_homepage_from_name = PREFIXES_DSW + query_mbox_homepage_from_name
    return query(t_query_mbox_homepage_from_name % name, DSW_SPARQL_ENDPOINT)


def get_dsw_person(name):
    query_person_data_from_name = """
    SELECT DISTINCT ?uri ?name ?homepage ?mbox_sha1sum ?workplaceHomepage 
                    ?affiliation ?based_near ?familyName ?givenName
    WHERE { 
        ?uri a foaf:Person;
             foaf:name ?name. 
        OPTIONAL {?uri foaf:familyName ?homepage}.
        OPTIONAL {?uri foaf:familyName ?familyName}.
        OPTIONAL {?uri foaf:givenName ?givenName}.
        OPTIONAL {?uri foaf:mbox_sha1sum ?mbox_sha1sum}.
        OPTIONAL {?uri foaf:workplaceHomepage ?workplaceHomepage}.
        OPTIONAL {?uri swrc:affiliation ?affiliation}.
        OPTIONAL {?uri foaf:based_near ?based_near}.
        FILTER regex(?name, "%s", "i" ) 
    }
    """
    t_query_person_data_from_name = PREFIXES_DSW + query_person_data_from_name
    return query(t_query_person_data_from_name % name,
                               DSW_SPARQL_ENDPOINT)

def get_dsw_author_papers(dsw_url):
    query_get_authors_papers_from_dsw = """
    SELECT DISTINCT * WHERE {
        ?paper dcterms:partOf <%s>;
               dc:title ?paperlabel;
               foaf:maker ?author.
        ?author foaf:name ?authorname.
    }
    """
    t_query_get_authors_papers_from_dsw = PREFIXES_DSW + \
    query_get_authors_papers_from_dsw
    dsw_authors_papers = query(t_query_get_authors_papers_from_dblp % \
                                  dsw_url, DSW_SPARQL_ENDPOINT)
                                
def get_dsw_organization_from_name(name):
    query_organization_data_from_name = """
    SELECT DISTINCT ?uri ?name
    WHERE { 
        ?uri a foaf:Organization;
             foaf:name ?name. 
        FILTER regex(?name, "%s", "i" ) 
    }
    """
    t_query_organization_data_from_name = PREFIXES_DSW + query_organization_data_from_name
    return query(t_query_organization_data_from_name % name,
                               DSW_SPARQL_ENDPOINT)

def get_dsw_organization_from_uri(uri):
    query_organization_data_from_uri = """
    SELECT DISTINCT ?name
    WHERE { 
        <%s> a foaf:Organization;
             foaf:name ?name.
    }
    """
    t_query_organization_data_from_uri = PREFIXES_DSW + query_organization_data_from_uri
    return query(t_query_organization_data_from_uri % uri,
                               DSW_SPARQL_ENDPOINT)
