from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import requests
import json
from xml.dom import minidom
from xml.dom.minidom import Document
import xml.etree.ElementTree as ET
import time
import os


def jprint(obj):
    # print a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


#get list of reports from MLA API
# response = requests.get("http://statistics.mla.com.au/ReportApi/GetReportList")
# report_details = response.json()['ReturnValue']
# print(response.status_code)
# #jprint(report_details)
#
# for report in report_details:
#     print("Name: " + report['Name'] + ", GUid: " + report["ReportGuid"])
#
#     parameters = report['Parameters']
#     paramstr = 'Parameters: '
#     for parameter in parameters:
#         paramstr += ', ' + parameter['ParameterName']
#     print(paramstr)



report_name = "Australia - EYCI and ESTLI - Daily"
id = "200deaa4-6a96-4fe6-b67b-2f4c99aee8c5"
Guid_dict = {}
response = requests.get("http://statistics.mla.com.au/ReportApi/GetReportList")
report_details = response.json()['ReturnValue']

#check that the get request worked
if response.status_code != 200:
    print("Exception when accessing MLA website")
else:
    print("MLA website access successful")

#make dictionary of Guids with names of reports
for report in report_details:
    Guid_dict[report['Name']] = report["ReportGuid"]

#get the return value xml text from the API
Base_URL = "http://statistics.mla.com.au/ReportApi/RunReport"
Query_String = "?ReportGuid=" + Guid_dict[report_name] + "&FromDate=" + "01%2F01%2F2019" + "&ToDate=" + "03%2F12%2F2019"
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
    #access node with required data
    for i in range(4):
        EYCIroot = EYCIroot[0]
    # attribute will be of None type if no indo is present
    if (type(EYCIroot.attrib.get('ConvertedData')) == str):
        EYCI_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = EYCIroot.attrib.get('ConvertedData')


for key,value in EYCI_dict.items():
    print(key, value)

#upload data to amphora data website
configuration = Configuration()
auth_api = amphora_client.AuthenticationApi(amphora_client.ApiClient(configuration))
token_request = amphora_client.TokenRequest(username=os.getenv('username'), password=os.getenv('password') )

try:
    # Gets a token
    res = auth_api.authentication_request_token(token_request = token_request)
    configuration.api_key["Authorization"] = "Bearer " + res
    # create an instance of the Users API, now with Bearer token
    users_api = amphora_client.UsersApi(amphora_client.ApiClient(configuration))
    me = users_api.users_read_self()
    print(me)
except ApiException as e:
    print("Exception when calling AuthenticationAPI: %s\n" % e)

amphora_api = amphora_client.AmphoraeApi(amphora_client.ApiClient(configuration))

signals = []

try:
    for key,value in EYCI_dict.items():
        s = {'t': key, 'price': float(value)}
        signals.append(s)
    print(signals)
    amphora_api.amphorae_upload_signal_batch(id, request_body = signals)
except ApiException as e:
    print("Exception when calling AmphoraeApi: %s\n" % e)
