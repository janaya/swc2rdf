f = open('../rr2008-temp-data/rr2008-papers.txt','r')
of = open('../rr2008-data/rr2008-papers.csv','w')
l=' '
while l != '':
    l = f.readline()
    l = l.strip()
    authors, title = l.split('.')
    authors = authors.strip()
    title = title.strip()

    authors = authors.split(', ')

    if len(authors[len(authors)-1].split('and ')) > 1: 
        lasts = authors[len(authors)-1].split(' and ')
        authors[len(authors)-1]= lasts[0]
        authors.append(lasts[1])

    authors_names=[]
    for a in authors:
        print a
        authors_names.append(a.split()[0])
        authors_names.append(' '.join(a.split()[1:]))
        authors_names.append('')
        authors_names.append('')
        authors_names.append('')
    while len(authors_names) < 80:
        authors_names.append('')
    csvl=title+";"+";".join(authors_names)+"\n"
    of.write(csvl)
    
f.close()
of.close()
