f = open('temp_commite_rr2009.txt','r')
of = open('temp_commite_rr2009.csv','w')
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
