f = open('temp_commite_rr2008.txt','r')
of = open('temp_commite_rr2008.csv','w')
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
    csvl=";"+firstname+";"+lastname+";"+affiliation+"\n"
    of.write(csvl)
    
f.close()
of.close()
