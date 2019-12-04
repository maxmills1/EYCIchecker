import requests
import json
from xml.dom import minidom
from xml.dom.minidom import Document
import xml.etree.ElementTree as ET

def jprint(obj):
    # print a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
'''
response = requests.get("http://statistics.mla.com.au/ReportApi/GetReportList")
report_details = response.json()['ReturnValue']
print(response.status_code)
#jprint(report_details)

for report in report_details:
    print("Name: " + report['Name'] + ", GUid: " + report["ReportGuid"])

    parameters = report['Parameters']
    paramstr = 'Parameters: '
    for parameter in parameters:
        paramstr += ', ' + parameter['ParameterName']
    print(paramstr)
'''






report_name = "Australia - EYCI and ESTLI - Daily"
Guid_dict = {}
response = requests.get("http://statistics.mla.com.au/ReportApi/GetReportList")
report_details = response.json()['ReturnValue']
#check that the get request worked
print(response.status_code)

#make dictionary of Guids with names of reports
for report in report_details:
    Guid_dict[report['Name']] = report["ReportGuid"]

#get the return value xml text from the API
Base_URL = "http://statistics.mla.com.au/ReportApi/RunReport"
Query_String = "?ReportGuid=" + Guid_dict[report_name] + "&FromDate=" + "13%2F11%2F2019" + "&ToDate=" + "03%2F12%2F2019"
response = requests.get(Base_URL + Query_String)
return_value = response.json()['ReturnValue']

#make xml doc object and make pretty
xmldoc = minidom.parseString(return_value)
pretty_xml_as_string = xmldoc.toprettyxml()
#print(pretty_xml_as_string)

#make element tree from xml string
root = ET.fromstring(return_value)
calroot = root

EYCI_dict = {}

#get calendar date collection node
for i in range(4):
    calroot = calroot[0]
for child in calroot:
    EYCIroot = child
    #print(child.attrib.get('CalendarDate'))
    for i in range(4):
        EYCIroot = EYCIroot[0]
    if (type(EYCIroot.attrib.get('ConvertedData')) == str):
        EYCI_dict[child.attrib.get('CalendarDate')] = EYCIroot.attrib.get('ConvertedData')

for key,value in EYCI_dict.items():
    print(key, value)
