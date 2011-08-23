f = open('data_swaml2010.txt','r')
of = open('data_swaml2010.csv','w')
l=' '
while l != '':
    l = f.readline()
    l = l.strip()
    l = l.replace('* ','')
    title = l.split(' (')[0]

    l = f.readline()
    l= l.strip().rstrip('.')
    authors=l.split(', ')
    if len(authors[len(authors)-1].split('and ')) > 1: 
        lasts = authors[len(authors)-1].split(' and ')
        authors[len(authors)-1]= lasts[0]
        authors.append(lasts[1])
    #authors_dict = [{'first_name':a.split(' ')[0].strip(), 'last_name':a.split(' ')[1].strip()} for a in authors]
    authors_names=[]
    for a in authors:
        print a
        authors_names.append(a.split(' ')[0])
        authors_names.append(a.split(' ')[1])
        authors_names.append('')
        authors_names.append('')
        authors_names.append('')
    while len(authors_names) < 80:
        authors_names.append('')
    csvl=title+";"+";".join(authors_names)+"\n"
    of.write(csvl)
    
f.close()
of.close()
