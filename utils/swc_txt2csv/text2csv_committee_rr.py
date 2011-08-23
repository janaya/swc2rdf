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

def txt2csv_committee_rr(txtfile, csvfile, querydsw = False):
    f = open(txtfile,'r')
    of = open(csvfile,'w')
    l=' '
    while l != '':
        l = f.readline()
        l = l.strip()
        print l
        name = l.split(" (")[0].split(", ")[0]
        affiliation = ', '.join(l.split(" (")[0].split(", ")[1:])
        print name
        firstname = name.split()[0]
        lastname = ' '.join(name.split()[1:])

        _, mbox_sha1sum, homepage = query(t_query_mbox_homepage_from_name % name)

    #    csvl=";"+firstname+";"+lastname+";"+affiliation+"\n"
        csvl=";"+firstname+";"+lastname+";"+affiliation+";"+mbox_sha1sum";"+homepage+"\n"
        of.write(csvl)
    f.close()
    of.close()

def main(argv):
    txtfile = 'temp_commite_rr2009.txt'
    csvfile = 'temp_commite_rr2009.csv'
    txt2csv_committee_rr(txtfile, csvfile, True)

if __name__ == "__main__":
    main(sys.argv[1:])
