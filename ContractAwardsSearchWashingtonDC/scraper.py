# -*- coding: utf-8 -*-
import re
import json
import datetime
import turbotlib
import requests
from bs4 import BeautifulSoup

def parse_date(s):
    return datetime.datetime.strptime(s.strip(), "%m/%d/%Y")

def pr_date(d):
    return d.strftime("%Y-%m-%d")

turbotlib.log("Starting run...") # Optional debug logging

def total_records():
    url = "http://app.ocp.dc.gov/RUI/information/award/search_results.asp"
    resp = requests.get(url)
    doc = BeautifulSoup(resp.content)
    num = re.search("Total Contract Awards: ([0-9]+)", doc.find('div', class_="contentContainer").find('table').find('td').text)
    return int(num.group(1))


url_template="http://app.ocp.dc.gov/RUI/information/award/award_detail.asp?award_id="

n=1
t = total_records()

turbotlib.log("Attempting to collect " + str(t) + " records.")
while t > 0:
    current_url = url_template + str(n)
    response = requests.get(current_url)
    if not response.ok:
        n += 1
        continue
    doc = BeautifulSoup(response.content)
    tds = doc.find('div',class_="contentContainer").find_all('td')
    data = {
        "source_url": current_url,
        "sample_date":pr_date(datetime.datetime.now()),
        "number":n,
        "Agency": tds[2].text.strip(),
        "Post Date": pr_date(parse_date(tds[4].text)),
        "Agency Director/Contact": {
            "Name": tds[6].text.strip(),
            "Telephone": tds[8].text.strip(),
            "Email": tds[10].text.strip()
        },
        "Contracting Officer": {
            "Name": tds[12].text.strip(),
            "Telephone": tds[14].text.strip(),
            "Email": tds[16].text.strip()
        },
        "COTR": {
            "Name": tds[18].text.strip(),
            "Telephone": tds[20].text.strip(),
            "Email": tds[22].text.strip()
        },
        "Contract Specialist":{
            "Name": tds[24].text.strip(),
            "Telephone": tds[26].text.strip(),
            "Email": tds[28].text.strip()
        },
        "Commodity/Group Number": tds[30].text.strip(),
        "NIGP Code":tds[32].text.strip(),
        "Description": tds[34].text.strip(),
        "Contract Type":tds[36].text.strip(),
        "Solicitation Number": tds[38].text.strip(),
        "Contract Number": tds[40].text.strip(),
        "Contract Amount": tds[42].text.strip(),
        "Recurring Contract": bool(re.search("Yes", tds[43].text.strip())),
        "Contract Start": pr_date(datetime.datetime.strptime(tds[45].text.split("-")[0].strip(), "%m/%d/%y")),
        "Contract End": pr_date(datetime.datetime.strptime(tds[45].text.split("-")[1].strip(), "%m/%d/%y")),
        "Multi-Year": tds[47].text.strip(),
        "Contract Year": tds[49].text.strip(),
        "Market Type": tds[51].text.strip(),
        "Not For Profit": tds[53].text.strip(),
        "LSDBE": map(lambda x: x.strip(),re.sub("\s{2,}",",",tds[55].text.strip()).split(",")),
        "Business Name": tds[58].text.strip(),
        "Contractor Name": tds[60].text.strip(),
        "Email": tds[62].text.strip(),
        "Address": tds[64].text.strip(),
        "City": tds[66].text.strip(),
        "State": tds[68].text.strip().split(",")[0].strip(),
        "Zip": tds[68].text.strip().split(",")[1].strip(),
        "Phone": tds[70].text.strip(),
        "Fax": tds[72].text.strip(),
        "Comments": tds[74].text.strip()
    }

    # The Turbot specification simply requires us to output lines of JSON
    print json.dumps(data)
    n += 1
    t -= 1


turbotlib.log(str(n-1) + " items scraped.")
