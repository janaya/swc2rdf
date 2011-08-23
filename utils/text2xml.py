from xml.dom.minidom import Document


doc = Document()
snapshot = doc.createElement("snapshot")
doc.appendChild(snapshot)
submissions = doc.createElement("submissions")
snapshot.appendChild(submissions)

paper_number = "1"
is_paper = "yes"
decision = "accept"
abstract = country = affiliation = homepage = email = keyword = url = ""

f = open('data_rr2010.txt','r')
for l in f.readlines():

    l = l.replace('    * ','')
    l = l.replace('\n','')
    print l
#    authors, title = l.split('. ')
    authors = l.split('. ')[0]
    try:
        title = l.split('. ')[1]
    except:
        title=""
#    if title.split(' (') > 1:
#        title, paper_type = title.split(' (')
    title = title.rstrip(' (')
    title.strip()
    authors = authors.split(', ')
    if len(authors[len(authors)-1].split('and ')) > 1: 
        authors[len(authors)-1]=authors[len(authors)-1].split('and ')[1]
    authors = [{'first_name':a.split(' ')[0].strip(), 'last_name':a.split(' ')[1].strip()} for a in authors]

    submission = doc.createElement("submission")
    submission.setAttribute("number", paper_number)
    submission.setAttribute("paper", is_paper)
    submissions.appendChild(submission)
    xml_title = doc.createElement("title")
    submission.appendChild(xml_title)
    xml_title_text = doc.createTextNode(title)
    xml_title.appendChild(xml_title_text)
    xml_abstract = doc.createElement("abstract")
    submission.appendChild(xml_abstract)
    xml_abstract_text = doc.createTextNode(abstract)
    xml_abstract.appendChild(xml_abstract_text)

    xml_authors = doc.createElement("authors")
    submission.appendChild(xml_authors)

    for author in authors:
        xml_author = doc.createElement("author")
        xml_authors.appendChild(xml_author)
        first_name = doc.createElement("first_name")
        xml_author.appendChild(first_name)
        first_name_text = doc.createTextNode(author['first_name'])
        first_name.appendChild(first_name_text)
        last_name = doc.createElement("last_name")
        xml_author.appendChild(last_name)
        last_name_text = doc.createTextNode(author['last_name'])
        last_name.appendChild(last_name_text)
        xml_country = doc.createElement("country")
        xml_author.appendChild(xml_country)
        xml_country_text = doc.createTextNode(country)
        xml_country.appendChild(xml_country_text)
        xml_homepage = doc.createElement("homepage")
        xml_author.appendChild(xml_homepage)
        xml_homepage_text = doc.createTextNode(homepage)
        xml_homepage.appendChild(xml_homepage_text)
        xml_email = doc.createElement("email")
        xml_author.appendChild(xml_email)
        xml_email_text = doc.createTextNode(email)
        xml_email.appendChild(xml_email_text)
        xml_affiliation = doc.createElement("affiliation")
        xml_author.appendChild(xml_affiliation)
        xml_affiliation_text = doc.createTextNode(affiliation)
        xml_affiliation.appendChild(xml_affiliation_text)

    xml_keywords = doc.createElement("keywords")
    submission.appendChild(xml_keywords)

    xml_keyword = doc.createElement("keyword")
    xml_keywords.appendChild(xml_keyword)
    xml_keyword_text = doc.createTextNode(keyword)
    xml_keyword.appendChild(xml_keyword_text)

    xml_url = doc.createElement("url")
    submission.appendChild(xml_url)
    xml_url_text = doc.createTextNode(url)
    xml_url.appendChild(xml_url_text)

    xml_decision = doc.createElement("decision")
    submission.appendChild(xml_decision)
    xml_decision_text = doc.createTextNode(decision)
    xml_decision.appendChild(xml_decision_text)


print(doc.toprettyxml(indent="  ", encoding="utf-8"))

f.close()

