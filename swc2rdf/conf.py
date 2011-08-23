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


# Endpoints
DBLP_SPARQL_ENDPOINT = "http://dblp.l3s.de/d2r/sparql"
#DBLP_SPARQL_ENDPOINT = "http://www4.wiwiss.fu-berlin.de/dblp/sparql"
#http://www4.wiwiss.fu-berlin.de/dblp/snorql/
DSW_SPARQL_ENDPOINT = "http://data.semanticweb.org/sparql"

# Conference URIs
DSW_BASE_URL = "http://data.semanticweb.org"
DSW_PERSON_BASE_URL = DSW_BASE_URL + "/person"
DSW_URL = DSW_BASE_URL + "/conference/%s/%s"
DSW_COMPLETEGRAPH_URL = DSW_URL + "/complete"
DSW_PROCEEDINGS_URL = DSW_URL + "/proceedings"
DSW_PROCEEDINGS_EDITORLIST_URL = DSW_PROCEEDINGS_URL + "/editor_list"
DSW_PAPER_BASE_URL = DSW_URL + "/paper"
DSW_CHAIR_ROLE_BASE_URL = DSW_URL + "/chair"


DBLP_BASE_URL = "http://dblp.l3s.de/d2r/resource"
DBLP_PERSON_BASE_URL = DBLP_BASE_URL + "authors/"
DBLP_URL = DBLP_BASE_URL + "/publications/conf/%s/%s" 
DBLP_CONFSERIES_BASE_URL = DBLP_BASE_URL + "conferences/%s"
DBLP_PAPER_BASE_URL = DBLP_BASE_URL + "/publications/conf/%s"
