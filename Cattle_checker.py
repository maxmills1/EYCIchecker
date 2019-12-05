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
import datetime
import os


def jprint(obj):
    # print a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

#turn date to string formatted so that the MLA API accepts
def d_to_string(d):
    datestring = '{:02d}'.format(d.day) + '%2F' + '{:02d}'.format(d.month) + '%2F' + '{:02d}'.format(d.year)
    return datestring


report_name = "Australia - Live export cattle prices - Weekly"
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
DATE_RANGE = 21 #21 as report is weekly
today = datetime.date.today()
start_date = today - datetime.timedelta(days=DATE_RANGE)

#get the return value xml text from the API
Base_URL = "http://statistics.mla.com.au/ReportApi/RunReport"
Query_String = "?ReportGuid=" + Guid_dict[report_name] + "&FromDate=" + \
    d_to_string(start_date) + "&ToDate=" + d_to_string(today)
response = requests.get(Base_URL + Query_String)
return_value = response.json()['ReturnValue']

# #make xml doc object and make pretty
# xmldoc = minidom.parseString(return_value)
# pretty_xml_as_string = xmldoc.toprettyxml()
# print(pretty_xml_as_string)

D_steers_dict = dict()
D_heifers_dict = dict()
T_steers_dict = dict()
T_heifers_dict = dict()

#make element tree from xml string
root = ET.fromstring(return_value)
calroot = root

#get calendar date collection node
for i in range(4):
    calroot = calroot[0]

for child in calroot:
    collection_node = child
    date = child.attrib.get('CalendarMonth').replace('T', ' ')
    print(date)
    #access node with required data
    for i in range(5):
        collection_node = collection_node[0]
    #reached nodes of orign cities
    for city in collection_node:
        #Api contains no data for Broome so skip to Tville & Dwin
        if city.get('AttributeName5') == "Broome":
            continue
        type_node = city[0]
        #find data for each type of cow
        for cow_type in type_node:
            data = cow_type[0][1].get('ConvertedData')


            # attribute will be of None type if no info is present
            if (type(data) != str):
                continue

            #put the data into the corresponding dicts
            if city.get('AttributeName5') == "Darwin":
                if cow_type.get('AttributeName3') == "Steer":
                    D_steers_dict[date] = data
                elif cow_type.get('AttributeName3') == "Heifer":
                    D_heifers_dict[date] = data
            elif city.get('AttributeName5') == "Townsville":
                if cow_type.get('AttributeName3') == "Steer":
                    T_steers_dict[date] = data
                elif cow_type.get('AttributeName3') == "Heifer":
                    T_heifers_dict[date] = data


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

#make dict and id list correspond to Amphora id
dict_list = [D_heifers_dict, D_steers_dict, T_heifers_dict, T_steers_dict]
id_list = ["39b611f2-0e28-4eac-a2a8-da38f9100894", "152f2e2a-ff0a-41d9-ad0e-61f3b25e0248",
    "61f7f692-8c4e-4abd-a365-4a8d08efd79f", "673e043d-8921-4879-a500-4463d57f2767"]

D_steers_id = "152f2e2a-ff0a-41d9-ad0e-61f3b25e0248"
D_heifers_id = "39b611f2-0e28-4eac-a2a8-da38f9100894"
T_steers_id = "673e043d-8921-4879-a500-4463d57f2767"
T_heifers_id = "61f7f692-8c4e-4abd-a365-4a8d08efd79f"


for i in range(len(dict_list)):
    signals = []
    try:
        for key,value in dict_list[i].items():
            s = {'t': key, 'price': float(value)}
            signals.append(s)
        print(signals)
        amphora_api.amphorae_upload_signal_batch(id_list[i], request_body = signals)
    except ApiException as e:
        print("Exception when calling AmphoraeApi: %s\n" % e)
