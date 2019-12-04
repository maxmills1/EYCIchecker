from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import requests
import xml.etree.ElementTree as ET
import time
import os
import datetime

id = "200deaa4-6a96-4fe6-b67b-2f4c99aee8c5"

#turn date to string formatted so that the MLA API accepts
def d_to_string(d):
    datestring = '{:02d}'.format(d.day) + '%2F' + '{:02d}'.format(d.month) + '%2F' + '{:02d}'.format(d.year)
    return datestring

#get report details from MLA API
report_name = "Australia - EYCI and ESTLI - Daily"
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

#set date range to upload, starting from current day
DATE_RANGE = 3
today = datetime.date.today()
start_date = today - datetime.timedelta(days=DATE_RANGE)

#get the return value xml text from the API
Base_URL = "http://statistics.mla.com.au/ReportApi/RunReport"
Query_String = "?ReportGuid=" + Guid_dict[report_name] + "&FromDate=" + \
    d_to_string(start_date) + "&ToDate=" + d_to_string(today)
response = requests.get(Base_URL + Query_String)
return_value = response.json()['ReturnValue']

#make element tree from xml string
root = ET.fromstring(return_value)
EYCI_dict = {}

try:
    #get calendar date collection node
    calroot = root
    for i in range(4):
        calroot = calroot[0]
    for child in calroot:
        EYCIroot = child
        #access node with required data
        for i in range(4):
            EYCIroot = EYCIroot[0]
        # attribute will be of None type if no info is present
        if (type(EYCIroot.attrib.get('ConvertedData')) == str):
            EYCI_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = EYCIroot.attrib.get('ConvertedData')
except Exception as e:
    print("no data entries")
    exit()

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
except ApiException as e:
    print("Exception when calling AuthenticationAPI: %s\n" % e)

amphora_api = amphora_client.AmphoraeApi(amphora_client.ApiClient(configuration))

#list of dictionaries with signal values
signals = []

try:
    for key,value in EYCI_dict.items():
        s = {'t': key, 'price': float(value)}
        signals.append(s)

    amphora_api.amphorae_upload_signal_batch(id, request_body = signals)
except ApiException as e:
    print("Exception when calling AmphoraeApi: %s\n" % e)
