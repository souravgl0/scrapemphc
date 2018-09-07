import sys
import os
import requests
from bs4 import BeautifulSoup as bs

url = "http://district.mphc.gov.in/%E0%A4%A8%E0%A4%BF%E0%A4%B0%E0%A5%8D%E0%A4%A3%E0%A4%AF-%E0%A4%86%E0%A4%A6%E0%A5%87%E0%A4%B6"
path = "data/"

def getjudgeurllist():
    html = s.get(url)
    soup =  bs(html.content,'lxml')
    select = soup.find("select", {"id": "seljug"})
    optionlist = select.find_all("option")

    def returnurl(court_no):
        return "http://district.mphc.gov.in/php/dc/Judgment/get_judgment.php?court_no="+court_no+"&language=hi"

    rurl=[]
    for option in optionlist:
        rurl.append((option.text,returnurl(option.attrs['value'])))

    return rurl

def parsejudgedata(url):
    orderlist=[]
    judgementlist=[]

    a = s.get(url)
    # print "this  got  done  "
    soup =  bs(a.content,'lxml')
    table=soup.find_all("table")
    if len(table)==0:
        return [],[]
    table = table[0]

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols)>=4:
            text = cols[4].text
            if "ORDER" in text:
                orderlist.append(str(cols[4].a.attrs['href']))
            if "Judgment" in text:
                judgementlist.append(str(cols[4].a.attrs['href']))
    return orderlist,judgementlist

if not os.path.exists(path):
    os.makedirs(path)


def downloaddistrict(path,start):
    rurl = getjudgeurllist()

    num_judge = len(rurl)
    docs = 0
    for i,url in enumerate(rurl[start-1:],start):
        orderlist,judgementlist = parsejudgedata(url[1])
        length = len(orderlist)+len(judgementlist)
        if length == 0:
            continue

        docs += length

        fpath = os.path.join(path,url[0])
        try:
            if not os.path.exists(fpath):
                os.mkdir(fpath)
        except OSError as exc:
            if exc.errno == 36:
                fpath = os.path.join(path,url[0][:50])
                os.mkdir(fpath)

        if not os.path.exists(os.path.join(fpath,"Orders")):
            os.mkdir(os.path.join(fpath,"Orders"))
        if not os.path.exists(os.path.join(fpath,"Judgements")):
            os.mkdir(os.path.join(fpath,"Judgements"))

        print ("%d/%d" % (i,num_judge) )," Judges ",url[0]," Number of Docs: ",length

        for i,doc in enumerate(orderlist,1):
            with open(os.path.join(fpath,"Orders",str(i)+".pdf"),"wb") as f:
                f.write(requests.get(doc).content)
            sys.stdout.write('\r')
            sys.stdout.write(" %d/%d Downloaded" % (i,length))
            sys.stdout.flush()

        for i,doc in enumerate(judgementlist,1):
            with open(os.path.join(fpath,"Judgements",str(i)+".pdf"),"wb") as f:
                f.write(requests.get(doc).content)
            sys.stdout.write('\r')
            sys.stdout.write(" %d/%d Downloaded" % (i+len(orderlist),length))
            sys.stdout.flush()
        print

    print str(docs) + " documents Downloaded"


s = requests.Session()
s.get(url)

html = s.get(url)
soup =  bs(html.content,'lxml')
select = soup.find("select", {"id": "menu_dist1"})
optionlist = select.find_all("option")
distlist = [option.attrs['value'] for option in optionlist]

for i,dist in enumerate(distlist[3:],4):
    if i == 4:
        start = 46
    else:
        start = 1
    s.cookies['menu_distname'] = dist
    print ("%d/%d" % (i,len(distlist)) )," Districts ",dist
    if not os.path.exists(os.path.join(path,dist)):
        os.mkdir(os.path.join(path,dist))
    downloaddistrict(os.path.join(path,dist),start)

# set cookie
# rurl = getjudgeurllist()
