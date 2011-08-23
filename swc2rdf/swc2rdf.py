#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-
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
# dblp2dsw
#
# DESCRIPTION:
# Python functions to convert conferences plain data and DBLP RDF to DSW RDF
#
# TODO: 
"""
    dblp2dsw
    ~~~~~~~~~~~~~~~

    Python functions to convert conferences plain data and DBLP RDF to DSW RDF.
    Usage: execute ./dblp2dsw -h

    :author:       Julia Anaya
    :copyright:    author 
    :license:      GNU GPL version 3 or any later version 
                    (details at http://www.gnu.org)
    :contact:      julia dot anaya at gmail dot com
    :dependencies: python (>= version 2.6)
    :change log:
    
    .. TODO:: 
    * Create persons (chairs, editors, author with a unique function)
    * Which affiliation choose when there're severals
"""

__app__ = "dblp2dsw"
__author__ = "Julia Anaya"
__version__ = "0.0"
__date__ = "2010/12/19"
__copyright__ = "Copyright (c) 2010 Julia Anaya"
__license__ = " GNU GPL version 3 or any later version (details at http://www.gnu.org)"
__credits__ = ""

import sys
import getopt

from urllib2 import HTTPError
import logging
from rdflib import URIRef, Literal, BNode, ConjunctiveGraph
import csv, codecs, cStringIO
import unicodedata

from conf import *
from namespaces import *
from dblp_queries import *
from dsw_queries import *
import os.path

##############################################################################
# Administrative functions
##############################################################################

def _usage():
    print "Usage: %s options" % __app__
    print """
Options:
  -h, --help      Print this usage message.
  -a, --acroname  Conference acronym name
  -p, --homepage  Conference homepage
  -y, --year      Conference year
  -m, --month     Conference month
  -t, --location  Conference location
  -c, --comitte   Conference chairs csv
  -r, --papers    Conference papers csv
  -v,             version
Example:
    %s -a rr -y 2010 -p http://www.inf.unibz.it/krdb/events/rr2010/ -c chairs_rr2010.csv
    %s -a swap -y 2010 -month September -conf_name "6th Workshop on Semantic Web Applications and Perspectives - Bressanone, Italy- Sep. 21-22, 2010" -p http://www.inf.unibz.it/krdb/events/swap2010/ -t "http://dbpedia.org/resource/Brixen" -r papers_swap2010.csv -c chairs_swap2010.csv
    %s -a swap

""" % __app__

def _version():
    """
    Display a formatted version string for the module
    """
    print """%(__app__)s %(__version__)s
%(__copyright__)s
released %(__date__)s

Thanks to:
%(__credits__)s""" % globals()


##############################################################################
# Global variables
##############################################################################

# Endpoints
############

#DBLP_SPARQL_ENDPOINT = "http://dblp.l3s.de/d2r/sparql"
DBLP_SPARQL_ENDPOINT = "http://www4.wiwiss.fu-berlin.de/dblp/sparql"
DSW_SPARQL_ENDPOINT = "http://data.semanticweb.org/sparql"

## Conference variables
#######################
#DBPL_BASE_URL = "http://dblp.l3s.de/d2r/resource"
#DSW_BASE_URL = "http://data.semanticweb.org"

#DBLP_CONFSERIES_BASE_URL = "http://dblp.l3s.de/d2r/page/conferences"

__all__ = [
# 'UTF8Recoder',
# 'UnicodeReader',
 'create_chair_graph',
 'create_graph',
 'create_organizations_graph',
 'create_paper_dsw_uri_from_dblp_uri',
 'create_person_dsw_uri_from_name',
 'create_rdf',
 'dblp2dsw',
 'dblp_conf_exists',
 'create_chair_graph',
 'get_csv_chairs',
 'get_csv_papers_authors',
 'get_dblp_author_papers',
 'get_dblp_data',
 'get_dblp_editors',
 'get_dblp_uri',
 'get_dblp_uri_year',
 'get_dblp_year',
 'get_dsw_authors',
 'get_dsw_editors',
 'get_dsw_organization_from_name',
 'get_dsw_organization_from_uri',
 'get_dsw_organizations',
 'get_dsw_papers',
 'get_dsw_person',
 'get_mbox_homepage_from_name',
 'name_from_given_family_name',
 'unicode_csv_reader',
 'unicodedata',
 'utf_8_encoder'
]


# Logging config
################  
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)

##############################################################################
# CSV functions
##############################################################################
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

##############################################################################
# Other functions
##############################################################################

def name_from_given_family_name(family_name, given_name):
    """Create author full name from given name and family name
    
    :param family_name: family name
    :param given_name: given name
    :type family_name: string
    :type given_name: string
    :return: full name
    :rtype: string
    
    """
    return unicodedata.normalize('NFKD', given_name.strip() + " " +\
                                  family_name.strip()).encode('ascii','ignore')



##############################################################################
# URIs creation or conversion functions
##############################################################################

def create_person_dsw_uri_from_name(dsw_person_base_url, person_name):
    """Create person DSW URI from name
    
    :param dsw_person_base_url: DSW person base URI
    :param person_name: full name
    :type dsw_person_base_url: string
    :type person_name: string
    :return: person DSW URI
    :rtype: string
    
    """
    person_uri = dsw_person_base_url + "/" +  \
                                        person_name.replace(" ", "-").lower()
    return person_uri

def create_paper_dsw_uri_from_dblp_uri(dsw_paper_base_url, paper_dblp_uri):
    """Create paper DSW URI from DBLP URI
    
    :param dsw_paper_base_url: DSW paper base URI
    :param paper_dblp_uri: DBLP paper base URI
    :type dsw_paper_base_url: string
    :type paper_dblp_uri: string
    :return: papser DSW URI
    :rtype: string
    
    """
    paper_uri = dsw_paper_base_url + "/" + paper_dblp_uri.split("/")[-1:][0]
    return paper_uri

##############################################################################
# URIs creation or conversion functions
##############################################################################

def get_dsw_papers(dblp_papers, dsw_paper_base_url):
    """Create papers DSW URI from DBLP URI and data
    
    :param dsw_paper_base_url: DSW paper base URI
    :param dblp_papers: DBLP papers uri and label 
    :type dsw_paper_base_url: string
    :type dblp_papers: dict # {"paperdblpuri":{"label":}}
    :return: papers DSW URI and data
    :rtype: dict # {"paperdblpuri":{"label":, "uri":, "seeAlso":}}
    
    """
    dsw_papers = {}
    for paperdblpuri, paperdict in dblp_papers.items():
        logging.debug("Processing paper: %s" % paperdict['label'])
        uri = create_paper_dsw_uri_from_dblp_uri(dsw_paper_base_url, 
                                                 paperdblpuri)
#        for author in paperdict['authors']:
#            dsw_author = get_dsw_person(author)
#            if dsw_author:
#                uri = dsw_author[0]['uri']
            
#        dsw_papers[uri] = dict(paperdict.items() + \
        dsw_papers[paperdblpuri] = dict(paperdict.items() + \
                               [('uri', uri)] + \
                               [('seeAlso', paperdblpuri)])
    return dsw_papers

def get_dsw_authors(dblp_authors, dsw_person_base_url):
    """Create authors DSW URI from DBLP URI and data
    
    :param dsw_person_base_url: DSW paper base URI
    :param dblp_authors: DBLP papers uri and label 
    :type dsw_person_base_url: string
    :type dblp_authors: dict # {"authordblpuri":{"label":}}
    :return: authorss DSW URI and data
    :rtype: dict # {"authordblpuri":{"name":, "uri":, "seeAlso":}}
    
    """
    dsw_authors = {}
    for authordblpuri, authordict in dblp_authors.items():
        logging.debug("Processing author: %s" % authordict['name'])
        #@FIXME: several results
        dsw_author = get_dsw_person(authordict['name'])
        if dsw_author:
            uri = dsw_author[0]['uri']
            dsw_data = dsw_author[0].items()
        else:
            uri = create_person_dsw_uri_from_name(dsw_person_base_url, 
                                    authordict['name'])
            dsw_data = []
#        dsw_authors[uri] = dict(authordict.items()  + \
        dsw_authors[authordblpuri] = dict(authordict.items()  + \
                                dsw_data + \
                                {'uri':uri}.items() + \
                                {'seeAlso': authordblpuri}.items())  
    return dsw_authors

def get_dsw_editors(dblp_editors, dsw_person_base_url):
    """Create authors DSW URI from DBLP URI and data
    
    :param dsw_person_base_url: DSW paper base URI
    :param dblp_editors: DBLP papers uri and label 
    :type dsw_person_base_url: string
    :type dblp_editors: dict # {"":{"name":}}
    :return: editors DSW URI and data
    :rtype: dict # {"editordblpuri":{"name":, "uri":, "seeAlso":}}
    
    """
    dsw_editors = {}
    for editor in dblp_editors:
        dsw_editor = get_dsw_person(editor['name'])
        #@FIXME: several results
        if dsw_editor:
            uri = dsw_editor[0]["uri"]
            dsw_data = dsw_editor[0].items()
        else:
            uri = create_person_dsw_uri_from_name(dsw_person_base_url, 
                                    editor['name'])
            dsw_data = {"name": editor["name"]}.items()
#        dsw_editors[uri] = dict(dsw_data + \
        dsw_editors[editor['uri']] = dict(dsw_data + \
                                {'uri':uri}.items() + \
                                {'seeAlso': editor["uri"]}.items())  
    return dsw_editors

def get_csv_chairs(chairfilepath, dsw_person_base_url, 
                        dsw_chair_role_base_url):
    chairs = {}
    roles = {}
    csvfile = open(chairfilepath, "rb" 'utf-8')
    #dialect = csv.Sniffer().sniff(csvfile.read(1024))
    #csvfile.seek(0)
    #reader = csv.reader(csvfile, dialect)
    #reader = csv.reader(csvfile, delimiter=';')
    #reader = unicode_csv_reader(csvfile, delimiter=';')    
    reader = UnicodeReader(csvfile, delimiter=';')
    headers = reader.next()
    for row in reader:
#        print row
        #for header, col in zip(headers,row):
        dsw_chair_label, dsw_chair_given_name, \
        dsw_chair_family_name, dsw_chair_affiliation, \
        dsw_chair_email, dsw_chair_homepage = row
        dsw_chair_role_url = dsw_chair_role_base_url + "/" + \
                             dsw_chair_label.replace(" ", "").lower()
        dsw_chair_name = name_from_given_family_name(dsw_chair_family_name,
                                                     dsw_chair_given_name)
        logging.debug("Processing chair: %s" % dsw_chair_name)
        chair = get_dsw_person(dsw_chair_name)
        if chair:
            dsw_chair_uri = chair[0]['uri']
            chairs[dsw_chair_uri] = \
                dict({'role': dsw_chair_role_url}.items()+\
                     chair[0].items())
        else:
            dsw_chair_uri = create_person_dsw_uri_from_name(dsw_person_base_url, 
                                              dsw_chair_name)
#            print dsw_chair_uri
            affiliation = get_dsw_organization_from_name(dsw_chair_affiliation)
#            print affiliation
            if affiliation:
                affiliation_uri = affiliation[0]['uri']
                chairs[dsw_chair_uri] = {'name': dsw_chair_name,
                                               'role': dsw_chair_role_url,
                                               'affiliation': affiliation_uri }
            else:
#                affiliation_uri = unicodedata.normalize('NFKD',
#                         dsw_chair_affiliation.strip.split(",")[-1]\
#                            .encode('ascii','ignore')
                chairs[dsw_chair_uri] = {'name': dsw_chair_name,
                                               'role': dsw_chair_role_url}
        if not roles.get('dsw_chair_role_url', None):
            roles[dsw_chair_role_url] = {'label': dsw_chair_label,
                                         'chairs' : [dsw_chair_uri]}
        elif dsw_chair_uri not in \
                                roles[dsw_chair_role_url]['chairs']:
            roles[dsw_chair_role_url]['chairs'].append(dsw_chair_uri)
    csvfile.close()
    return chairs, roles

def get_csv_papers_authors(papersfilepath, dsw_paper_base_url, 
                                dsw_person_base_url):
    papers_dict = {}
    csvfile = open(papersfilepath, "rb" 'utf-8')   
    reader = UnicodeReader(csvfile, delimiter=';')
    headers = reader.next()
    authors_dict = {}
    papers_dict = {}
    # To get more info from DBLP get_dblp_author_papers
    for row in reader:
#        logging.debug("Reading row:" )
#        logging.debug(row)
        if row:
            paper_type = row.pop(0)
            paper_id = row.pop(0)
            if paper_type:
                paper_uri = dsw_paper_base_url+"/"+paper_type+"/"+str(paper_id)
            else:
                paper_uri = dsw_paper_base_url+"/"+str(paper_id)
            paper_title = row.pop(0)
            paper_abstract = row.pop()
            # TODO: query and add more info (seealso) from DBLP
            papers_dict[paper_uri] = {'label': paper_title, 
                                      'abstract': paper_abstract, 
                                      'uri': paper_uri,
                                      'authors':[]}
#            authors_dict = {}
#            papers_dict = {}
            logging.debug("Processing paper: %s" % paper_title)
            for j in range(divmod(len(row),5)[0]):
                author_given_name = row.pop(0)
                author_family_name = row.pop(0)
                author_affiliation = row.pop(0)
                author_country = row.pop(0)
                author_email = row.pop(0)
                if author_given_name and author_family_name:
                    author_name = name_from_given_family_name(
                                                    author_family_name, 
                                                    author_given_name)
                    logging.debug("Processing author: %s" % author_name)
                    author = get_dsw_person(author_name)
                    #logging.debug(author)
                    if author:
                        author_uri = author[0]['uri']
                        author_dict = dict(author[0].items()+{'papers':[paper_uri]}.items())
                        if author_dict.get("seeAlso", None):
                            logging.debug("Author URI from dsw: %s" % author_dict["seeAlso"])
                    else:
                        author_uri = create_person_dsw_uri_from_name(dsw_person_base_url, 
                                                       author_name)
                        ##############
                        author_dict = {'name': author_name,
                                       'uri':  author_uri,
                                       'papers':[paper_uri]}
        #                organization = get_dsw_organization_from_name(name)
        #                if organization:
        #                    organization_uri = organization[0]['uri']
        #                    organization_name = organization[0]['name']
        #                    organizations_dict[organization_uri] = \
        #                        {'name': organization_name, 'members': [author_uri]}
        #                    author_dict['affiliation'] = organization_uri
        #                else:
        ##                    organization_uri = dsw_organization_base_url
        #                    pass
        #                if author_email:
        #                    author_dict['mbox_sha1sum'] = sha.new(uthor_email).hexdigest() 
        #                if author_country:
        #                    pass
                    if not author_uri in authors_dict:
                        authors_dict[author_uri]= author_dict
                    else:
                        authors_dict[author_uri]['papers'].append(paper_uri)
                    papers_dict[paper_uri]['authors'].append(author_uri)
    return papers_dict, authors_dict            



def get_csv_keynotes(keynotesfilepath, dsw_keynote_base_url, 
                                dsw_person_base_url):
    keynotes_dict = {}
    csvfile = open(keynotesfilepath, "rb" 'utf-8')   
    reader = UnicodeReader(csvfile, delimiter=';')
    headers = reader.next()
    authors_dict = {}
    keynotes_dict = {}
    # To get more info from DBLP get_dblp_author_keynotes
    for row in reader:
#        logging.debug("Reading row:" )
#        logging.debug(row)
        if row:
            keynote_id = row.pop(0)
            keynote_uri = dsw_keynote_base_url+"/"+str(keynote_id)
            keynote_title = row.pop(0)
            keynote_author = row.pop(0)
            keynote_author_affiliation = row.pop()
            keynote_abstract = row.pop()
            keynote_start = row.pop()
            keynote_end = row.pop()
            # TODO: query and add more info (seealso) from DBLP
            keynotes_dict[keynote_uri] = {'label': keynote_title, 
                                      'summary': keynote_abstract, 
                                      'uri': keynote_uri, 
                                      'start': keynote_start, 
                                      'end': keynote_end,
                                      'authors':[]}
#            authors_dict = {}
#            keynotes_dict = {}
            logging.debug("Processing keynote: %s" % keynote_title)
            author_name = name_from_given_family_name(
                                                keynote_author.split(" ")[0],
                                                keynote_author.split(" ")[1])
            ogging.debug("Processing author: %s" % author_name)
            author = get_dsw_person(author_name)
            logging.debug(author)
            if author:
                author_uri = author[0]['uri']
                author_dict = dict(author[0].items()+{'keynotes':[keynote_uri]}.items())
                if author_dict.get("seeAlso", None):
                    logging.debug("Author URI from dsw: %s" % author_dict["seeAlso"])
            else:
                author_uri = create_person_dsw_uri_from_name(dsw_person_base_url, 
                                               author_name)
                ##############
                author_dict = {'name': author_name,
                               'uri':  author_uri,
                               'keynotes':[keynote_uri]}
            if not author_uri in authors_dict:
                authors_dict[author_uri]= author_dict
            else:
                authors_dict[author_uri]['keynotes'].append(keynote_uri)
            keynotes_dict[keynote_uri]['authors'].append(author_uri)
    return keynotes_dict, authors_dict 

def get_dsw_organizations(dsw_authors, dsw_editors, 
                               dsw_chairs):
    organizations = {}
    for author_dict in dsw_authors.values():
        if author_dict.get("affiliation", None):
            if organizations.get(author_dict["affiliation"], None):
                logging.debug("Processing organization: %s" % author_dict["affiliation"])
                if not author_dict['uri'] in organizations[author_dict["affiliation"]]['members']:
                    organizations[author_dict["affiliation"]]['members']\
                        .append(author_dict['uri'])
            else:
                organization = get_dsw_organization_from_uri(author_dict["affiliation"])
#                print organization
                logging.debug("Processing organization: %s" % author_dict["affiliation"])
                organization_name = organization[0]
                organizations[author_dict["affiliation"]] = \
                    {'name': organization_name, 'members': [author_dict['uri']]}
    # editor_dict['uri']
    for chair, chair_dict in dsw_chairs.items():
        if chair_dict.get("affiliation", None):
            if organizations.get(chair_dict["affiliation"], None):
                logging.debug("Processing organization: %s" % chair_dict["affiliation"])
                if not chair in organizations[chair_dict["affiliation"]]['members']:
                    organizations[chair_dict["affiliation"]]['members']\
                        .append(chair)
            else:
                organization = get_dsw_organization_from_uri(chair_dict["affiliation"])
                logging.debug("Processing organization: %s" % chair_dict["affiliation"])
#                print organization
                organization_name = organization[0]
                organizations[chair_dict["affiliation"]] = \
                    {'name': organization_name, 'members': [chair]}
    return organizations

def create_chair_graph(graph, dsw_url, dsw_chairs, dsw_roles):
    for role in dsw_roles.keys():
        graph.add((URIRef(dsw_url), SWC["hasRole"], 
                   URIRef(role)))
    for chair_role, chair_role_dict in dsw_roles.items():
        graph.add((URIRef(chair_role), RDF.type, SWC["Chair"]))
        graph.add((URIRef(chair_role), RDFS["label"], 
                   Literal(chair_role_dict['label'])))
        graph.add((URIRef(chair_role), SWC["isRoleAt"], 
                   URIRef(dsw_url)))
        for chair in chair_role_dict['chairs']:
           graph.add((URIRef(chair_role), SWC["heldBy"], 
                   URIRef(chair)))
    for chair, chair_dict in dsw_chairs.items():
        graph.add((URIRef(chair), RDF.type, FOAF["Person"]))
        graph.add((URIRef(chair), SWC["holdsRole"], 
                   URIRef(chair_dict["role"])))
        graph.add((URIRef(chair), RDFS["label"], 
                   Literal(chair_dict["name"])))
        graph.add((URIRef(chair), FOAF["name"],
                   Literal(chair_dict["name"])))
        if chair_dict.get("affiliation", None):
            graph.add((URIRef(chair), SWRC["affiliation"], 
                       URIRef(chair_dict["affiliation"])))
        if chair_dict.get("mbox_sha1sum", None):
            graph.add((URIRef(chair), FOAF["mbox_sha1sum"], 
                       Literal(chair_dict["mbox_sha1sum"])))
        if chair_dict.get("based_near", None):
            graph.add((URIRef(chair), FOAF["based_near"], 
                       URIRef(chair_dict["based_near"])))
        if chair_dict.get("workplaceHomepage", None):
            graph.add((URIRef(chair), FOAF["workplaceHomepage"], 
                       URIRef(chair_dict["workplaceHomepage"])))
        if chair_dict.get("homepage", None):
            graph.add((URIRef(chair), FOAF["homepage"], 
                       URIRef(chair_dict["homepage"])))
    return graph

def create_organizations_graph(graph, dsw_organizations):
    for organization, organization_dict in dsw_organizations.items():
        graph.add((URIRef(organization), RDF.type, FOAF["Organization"]))
        graph.add((URIRef(organization), RDFS["label"], 
                   Literal(organization_dict['name'])))
        graph.add((URIRef(organization), FOAF["name"], 
                   Literal(organization_dict['name'])))
        for member in organization_dict['members']:
           graph.add((URIRef(organization), FOAF["member"], 
                   URIRef(member)))
    return graph

def create_tutorials_graph(graph, dsw_tutorials):
    for tutorial, tutorial_dict in dsw_tutorials.items():
        graph.add((URIRef(tutorial), RDF.type, SWC["TutorialEvent"]))
        graph.add((URIRef(tutorial), RDFS["label"], 
                   Literal(tutorial_dict['label'])))
        graph.add((URIRef(tutorial), ICAL["dstart"], 
                   Literal(tutorial_dict['dstart'])))
        graph.add((URIRef(tutorial), ICAL["dend"], 
                   Literal(tutorial_dict['dend'])))
        graph.add((URIRef(tutorial), ICAL["dsummary"], 
                   Literal(tutorial_dict['dsummary'])))
        graph.add((URIRef(tutorial), SWC["isSubEventOf"], 
                   Literal(tutorial_dict['isSubEventOf'])))
        

def create_keynotes_graph(graph, dsw_keynotes):
    for keynote, keynote_dict in dsw_keynotes.items():
        graph.add((URIRef(keynote), RDF.type, SWC["TalkEvent"]))
        graph.add((URIRef(keynote), RDFS["label"], 
                   Literal(keynote_dict['label'])))
        graph.add((URIRef(keynote), ICAL["dstart"], 
                   Literal(keynote_dict['dstart'])))
        graph.add((URIRef(keynote), ICAL["dend"], 
                   Literal(keynote_dict['dend'])))
        graph.add((URIRef(keynote), ICAL["dsummary"], 
                   Literal(keynote_dict['dsummary'])))
        graph.add((URIRef(keynote), SWC["isSubEventOf"], 
                   Literal(keynote_dict['isSubEventOf'])))

def create_invitedtalk_graph(graph, dsw_invitedtalks):
    for invitedtalk, invitedtalk_dict in dsw_invitedtalks.items():
        graph.add((URIRef(invitedtalk), RDF.type, SWC["TalkEvent"]))
        graph.add((URIRef(invitedtalk), RDFS["label"], 
                   Literal(invitedtalk_dict['label'])))
        graph.add((URIRef(invitedtalk), ICAL["dstart"], 
                   Literal(invitedtalk_dict['dstart'])))
        graph.add((URIRef(invitedtalk), ICAL["dend"], 
                   Literal(invitedtalk_dict['dend'])))
        graph.add((URIRef(invitedtalk), ICAL["dsummary"], 
                   Literal(invitedtalk_dict['dsummary'])))
        graph.add((URIRef(invitedtalk), SWC["isSubEventOf"], 
                   Literal(invitedtalk_dict['isSubEventOf'])))

def create_graph(dsw_url, acron, year, month, conf_name, homepage, city, 
                dblp_url, dsw_completegraph_url, 
                dsw_proceedings_url, dsw_proceedings_editorlist_url, 
                dsw_editors, dsw_papers, 
                dsw_authors, dsw_chairs, dsw_roles, 
                dsw_organizations):
    """Generate graph with chairs, roles, editors, papers, organizations
    
    :param acron: Conference acronym name
    :param year: Conference year
    :param month: Conference month
    :param conf_name: Conference name
    :param homepage: Conference homepage
    :param city: Conference city
    :param dblp_url:
    :param dsw_url:
    :param dsw_completegraph_url:
    :param dsw_proceedings_url:
    :param dsw_proceedings_editorlist_url:
    :param dsw_editors:
    :param dsw_papers:
    :param dsw_authors:
    :param dsw_chairs:
    :param dsw_roles:
    :param dsw_organizations:

    :type acron: string
    :type year: string
    :type month: string
    :type conf_name: string
    :type homepage: string
    :type city: string
    :type dblp_url: string
    :type dsw_url: string
    :type dsw_completegraph_url: string
    :type dsw_proceedings_url: string
    :type dsw_proceedings_editorlist_url: string
    :type dsw_editors:
    :type dsw_papers:
    :type dsw_authors:
    :type dsw_chairs:
    :type dsw_roles:
    :type dsw_organizations:

    """
    # Graph namespaces
    graph = ConjunctiveGraph()
    graph.bind('dc', DC)
    graph.bind('foaf', FOAF)
    graph.bind('geo', GEO)
    graph.bind('ical', ICAL)
    graph.bind('rdfs', RDFS)
    graph.bind('swc', SWC)
    graph.bind('swrc', SWRC)
    graph.bind('swrc_ext', SWRC_EXT)
    graph.bind('dc', DC)

    # Conference general info
    graph.add((URIRef(dsw_url), RDF.type, SWC["ConferenceEvent"]))
    graph.add((URIRef(dsw_url), SWC["hasAcronym"], Literal(acron)))
    if conf_name:
        graph.add((URIRef(dsw_url), RDFS["label"], Literal(conf_name)))
    if homepage:
        graph.add((URIRef(dsw_url), FOAF["homepage"], URIRef(homepage)))
    if city: 
        graph.add((URIRef(dsw_url), FOAF["based_near"], URIRef(city)))
    # @FIXME: !!!!!
    if dblp_url:
        graph.add((URIRef(dsw_url), RDFS["seeAlso"],URIRef(dblp_url)))


    graph.add((URIRef(dsw_url), SWC["completeGraph"], 
                URIRef(dsw_completegraph_url)))

    # Conference proceedings
    if dsw_papers:
        graph.add((URIRef(dsw_url), SWC["hasRelatedDocument"], 
                URIRef(dsw_proceedings_url)))
        graph.add((URIRef(dsw_proceedings_url), RDF.type, 
               SWRC["Proceedings"]))
    #    graph.add((URIRef(dsw_proceedings_url), SWRC["booktitle"], 
    #                        Literal(dblp_label)))
        graph.add((URIRef(dsw_proceedings_url), SWRC["year"], 
               Literal(year)))
        if month:
            print "month!!: %s" % month
            graph.add((URIRef(dsw_proceedings_url), SWRC["month"], 
                    Literal(month)))

    # Conference editors
    if dsw_editors:
        graph.add((URIRef(dsw_proceedings_url), SWRC_EXT["editorList"], 
                URIRef(dsw_proceedings_editorlist_url)))
        graph.add((dsw_proceedings_editorlist_url, RDF.type, RDF.Description))


        for editor, editor_dict in dsw_editors.items():
            graph.add((URIRef(dsw_proceedings_url), SWRC["editor"], 
                       URIRef(editor)))

            # @FIXME: create editor_list (same graph)
            graph.add((URIRef(dsw_proceedings_editorlist_url), RDF.li, 
                              URIRef(editor)))


    # Conference papers
    for paper, paper_dict in dsw_papers.items():
#        print paper
#        print paper_dict
        logging.debug("Creating graph for paper: %s" % paper_dict["label"])
        graph.add((URIRef(dsw_proceedings_url), SWC["hasPart"], 
                   URIRef(paper_dict['uri'])))
        graph.add((URIRef(paper_dict['uri']),
                   RDF.type, SWRC["InProceedings"]))
        graph.add((URIRef(paper_dict['uri']),
                   SWC["isPartOf"], URIRef(dsw_proceedings_url)))
        graph.add((URIRef(paper_dict['uri']),
                   DC["title"], Literal(paper_dict["label"])))
        graph.add((URIRef(paper_dict['uri']),
                   SWRC["year"], Literal(year)))
        if month: 
            graph.add((URIRef(paper_dict['uri']),
                   SWRC["month"], Literal(month)))
        if paper_dict.get("seeAlso", None):
            graph.add((URIRef(paper_dict['uri']),
                       RDFS["seeAlso"],URIRef(paper_dict['seeAlso'])))
        graph.add((URIRef(paper_dict['uri']),
                   SWRC_EXT["authorList"], URIRef(paper_dict['uri'] + "/authorlist")))
            
        graph.add((URIRef(paper_dict['uri'] + "/authorlist"), RDF.type, RDF.Description))

        for author in paper_dict["authors"]:
            graph.add((URIRef(paper_dict['uri']), DC["creator"], 
                       URIRef(dsw_authors[author]['uri'])))
            graph.add((URIRef(paper_dict['uri']), FOAF["maker"], 
                       URIRef(dsw_authors[author]['uri'])))
            graph.add((URIRef(paper_dict['uri']), SWRC["author"], 
                       URIRef(dsw_authors[author]['uri'])))

            # @FIXME: create authorlist graph
            graph.add((URIRef(paper_dict['uri'] + "/authorlist"), RDF.li, URIRef(dsw_authors[author]['uri'])))

    # Conference authors
    for author, author_dict in dsw_authors.items():
        logging.debug("Creating graph for author: %s" % author_dict["name"])
        graph.add((URIRef(author_dict['uri']), RDF.type, FOAF["Person"]))
        graph.add((URIRef(author_dict['uri']), RDFS["label"], 
                   Literal(author_dict["name"])))
        graph.add((URIRef(author_dict['uri']), FOAF["name"],
                   Literal(author_dict["name"])))
        if author_dict.get("seeAlso", None):
            graph.add((URIRef(author_dict['uri']), RDFS["seeAlso"],
                   URIRef(author_dict["seeAlso"])))
        if author_dict.get("affiliation", None):
            graph.add((URIRef(author_dict['uri']), SWRC["affiliation"], 
                       URIRef(author_dict["affiliation"])))
        if author_dict.get("mbox_sha1sum", None):
            graph.add((URIRef(author_dict['uri']), FOAF["mbox_sha1sum"], 
                       Literal(author_dict["mbox_sha1sum"])))
        if author_dict.get("based_near", None):
            graph.add((URIRef(author_dict['uri']), FOAF["based_near"], 
                       URIRef(author_dict["based_near"])))
        if author_dict.get("workplaceHomepage", None):
            graph.add((URIRef(author_dict['uri']), FOAF["workplaceHomepage"], 
                       URIRef(author_dict["workplaceHomepage"])))
        if author_dict.get("homepage", None):
            graph.add((URIRef(author_dict['uri']), FOAF["homepage"], 
                       URIRef(author_dict["homepage"])))
        #made
        for paper in author_dict['papers']:
            graph.add((URIRef(author_dict['uri']), FOAF['made'],
                       URIRef(dsw_papers[paper]['uri'])))


    # Conference editors
    #for editor, editor_dict in dsw_editors:
    #    graph.add((URIRef(editor_dict['uri']), SWC["holdsRole"], 
    #               URIRef()))


    # Conference organizations
    #dsw_organizations
    # Conference chairs
    #dsw_chairs

    #graph.add(())
    #graph.add(())
    return graph

def create_rdf(graph, acron, year):
    """Generate RDF/XML file from graph
    
    :param graph: Conference RDF graph
    :param acron: Conference acronym name
    :param year: Conference year

    :type graph: ConjunctiveGraph
    :type acron: string
    :type year: string
    
    """
    rdf=graph.serialize(format="pretty-xml", max_depth=2)
    path = acron + '-complete.rdf'
    f = open(path, 'w')
    f.write(rdf)
    f.close()    
    return rdf

def dblp2dsw(acron, year, month, conf_name, homepage, city, dblp_url, dsw_url, 
             dsw_paper_base_url, dsw_person_base_url, 
             dsw_completegraph_url, dsw_proceedings_url, 
             dsw_proceedings_editorlist_url, chair_role_base_url,
             chairfilepath, papersfilepath):
    """Generate RDF graph with chairs, roles, editors, papers, organizations
    
    :param acron: Conference acronym name
    :param year: Conference year
    :param month: Conference month
    :param conf_name: Conference name
    :param homepage: Conference homepage
    :param city: Conference city
    :param dblp_url:
    :param dsw_url:
    :param dsw_paper_base_url:
    :param dsw_person_base_url:
    :param dsw_completegraph_url:
    :param dsw_proceedings_url:
    :param dsw_proceedings_editorlist_url:
    :param chair_role_base_url:
    :param chairfilepath: Conference chairs csv path
    :param papersfilepath: Conference papers csv path

    :type acron: string
    :type year: string
    :type month: string
    :type conf_name: string
    :type homepage: string
    :type city: string
    :type dblp_url: string
    :type dsw_url: string
    :type dsw_paper_base_url: string
    :type dsw_person_base_url: string
    :type dsw_completegraph_url: string
    :type dsw_proceedings_url: string
    :type dsw_proceedings_editorlist_url: string
    :type chair_role_base_url: string
    :type chairfilepath: string
    :type papersfilepath: string

    """
    dsw_chairs = dsw_roles = dsw_editors = {}
    if papersfilepath:
        dsw_papers, dsw_authors = \
        get_csv_papers_authors(papersfilepath, dsw_paper_base_url, 
                                dsw_person_base_url)
    else:
        dblp_papers, dblp_authors = get_dblp_author_papers(dblp_url)
        dsw_papers = get_dsw_papers(dblp_papers, dsw_paper_base_url)
        dsw_authors = get_dsw_authors(dblp_authors, dsw_person_base_url)
        
    if chairfilepath:
        dsw_chairs, dsw_roles = get_csv_chairs(chairfilepath, 
                                dsw_person_base_url,chair_role_base_url)
    else:
        dblp_editors = get_dblp_editors(dblp_url)
        dsw_editors = get_dsw_editors(dblp_editors, dsw_person_base_url)

    if not (month or conf_name):
        conf_name, month = get_dblp_data(dblp_url)

    dsw_organizations = get_dsw_organizations(dsw_authors, 
                                dsw_editors, dsw_chairs)

#    if city:
#        

    graph = create_graph(dsw_url, acron, year, month, conf_name, homepage, city,
                dblp_url, dsw_completegraph_url, 
                dsw_proceedings_url, dsw_proceedings_editorlist_url, 
                dsw_editors, dsw_papers, 
                dsw_authors, dsw_chairs, dsw_roles, 
                dsw_organizations)
    graph = create_chair_graph(graph, dsw_url, dsw_chairs, dsw_roles)
    graph = create_organizations_graph(graph, dsw_organizations)

    create_rdf(graph, acron, year)

def main(argv):
    """
    Options:
      -h, --help      Print this usage message.
      -a, --acroname  Conference acronym name
      -n, --name      Conference name
      -p, --homepage  Conference homepage
      -y, --year      Conference year
      -m, --month     Conference month
      -t, --city      Conference city URI
      -c, --comitte   Conference chairs csv path
      -r, --papers    Conference papers csv path
      -v,             version
    Example:
        %s -a rr -y 2010 -p http://www.inf.unibz.it/krdb/events/rr2010/ -c chairs_rr2010.csv
        %s -a swap -y 2010 -month September -conf_name "6th Workshop on Semantic Web Applications and Perspectives - Bressanone, Italy- Sep. 21-22, 2010" -p http://www.inf.unibz.it/krdb/events/swap2010/ -t "http://dbpedia.org/resource/Brixen" -r papers_swap2010.csv -c chairs_swap2010.csv
        %s -a swap
        dblp2dsw.py -a rr -n "The Third International Conference on Web Reasoning and Rule Systems - October 25-26, 2009, Chantilly, Virginia, USA" -y 2009 -m October -p http://www.rr-conference.org/RR2009/ -c ../rr2009-data/chairs_rr2009.csv -r ../rr2009-data/papers_2009.csv
    """
    # Example conference
#    acron_name = "rr"
#    year = "2010"
#    month = "September"
#    homepage = "http://www.inf.unibz.it/krdb/events/rr2010/"
    # @FIXME: only for RR
#    homepage_base = "http://www.rr-conference.org/RR"
#    homepage = homepage_base + year

#    conf_name = "Proceedings of the 5th Workshop on Semantic Web Applications and Perspectives (SWAP2008), Rome, Italy, December 15-17, 2008 (xsd:string)"
#    chairfilepath = '/home/make/open/m-develop/conferences2rdf/rr2010-xls-data/chairs_rr2010.csv'
#    paperfilepath = '/home/make/open/m-develop/conferences2rdf/rr2010-xls-data/papers_rr2010.csv'

    acron_name = year = month = conf_name = homepage = city = None
    chairfilepath = paperfilepath = None

    if not argv:
        print "Using default values"
    short_opts = "hva:p:y:m:t:n:c:r:"
    long_opts = ["help","version", "acroname=","name=","homepage=",
                 "year=","month=","city=",
                 "chaircsvpath=","paperscsvpath="]
    try:                                
        opts, args = getopt.getopt(argv, short_opts, long_opts)
    except getopt.GetoptError:          
        _usage()                         
        sys.exit(0)   
    for opt, arg in opts:
        if opt in ("-h", "--help"):     
            _usage()                 
            sys.exit(0)
        if opt in ("-v", "--version"):     
            _version()                 
            sys.exit(0)
        elif opt in ("-a", "--acroname"):
            acron_name = arg
        elif opt in ("-n", "--name"):
            conf_name = arg
        elif opt in ("-p", "--homepage"):
            homepage = arg
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-m", "--month"):
            month = arg
        elif opt in ("-t","--city"):
            city = arg
        elif opt in ("-c", "--chaircsvpath"):
            chairfilepath = arg
            if not os.path.isfile(chairfilepath):
                print "%s does not exist" % chairfilepath
                sys.exit(0)
        elif opt in ("-r", "--paperscsvpath"):
            paperfilepath = arg
            if not os.path.isfile(paperfilepath):
                print "%s does not exist" % paperfilepath
                sys.exit(0)
    print acron_name, year, month, conf_name, homepage, city, chairfilepath, \
        paperfilepath

    if not acron_name:
        print "You must supply at least the conference acronym"
        sys.exit(0)
    if not year:
        dblp_confseries_url = DBLP_BASE_URL + "conferences/%s" % (acron_name)
        # get conf years
#        confs = get_dblp_uri_year(acron_name)
        yearrange = range(2007, 2010) # @FIXME: only for RR
#        yearrange = range(2005, 2008) # @FIXME: only for SWAP
    else: yearrange = [year]
    for year in yearrange:

        acron = acron_name.upper() + str(year)
        logging.debug("Processing conference: %s" % acron)

        # Conference URIs
        dsw_person_base_url = DSW_PERSON_BASE_URL
        dsw_url = DSW_BASE_URL + "/conference/%s/%s" % (acron_name, year)
        dsw_completegraph_url = dsw_url + "/complete"
        dsw_proceedings_url = dsw_url + "/proceedings"
        dsw_proceedings_editorlist_url = dsw_proceedings_url + "/editor_list"
        dsw_paper_base_url = dsw_url + "/paper"
        dsw_chair_role_base_url = dsw_url + "/chair"

        dblp_url = DBLP_BASE_URL + "/publications/conf/%s/%s" % (acron_name, year)

#        print paperfilepath
        dblp2dsw(acron, year, month, conf_name, homepage, city, dblp_url, dsw_url, 
                 dsw_paper_base_url, dsw_person_base_url, 
                 dsw_completegraph_url, dsw_proceedings_url, 
                 dsw_proceedings_editorlist_url, dsw_chair_role_base_url,
                 chairfilepath, paperfilepath)

if __name__ == "__main__":
    main(sys.argv[1:])
