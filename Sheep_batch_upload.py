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


report_name = "Australia - OTH lamb indicators - National - Weekly"
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
print(pretty_xml_as_string)


L_lamb_dict = dict()
M_T_lamb_dict = dict()
H_T_lamb_dict = dict()
H_lamb_dict = dict()

L_lamb_id = "fdf6cc1a-c2bc-4d22-a013-f697e6e16771"
M_T_lamb_id = "f8ea22f4-b08e-46e3-abb4-8721478b9f94"
H_T_lamb_id = "5fa13614-ac5a-4af7-a908-c6f8414f4b26"
H_lamb_id = "d4975810-85e7-44e3-998f-a69438f4ea49"


#make element tree from xml string
root = ET.fromstring(return_value)
calroot = root

#get calendar date collection node
for i in range(4):
    calroot = calroot[0]

for child in calroot:
    collection_node = child
    date = child.attrib.get('CalendarWeek').replace('T', ' ')
    print(date)
    #access node with required data
    for i in range(3):
        collection_node = collection_node[0]
    #reached nodes of orign cities
    for sheep_type in collection_node:
        type_name = sheep_type.get('AttributeName3')
        data = sheep_type[0][0].get('ConvertedData')

        # attribute will be of None type if no info is present
        if (type(data) != str):
            continue

        #put the data into the corresponding dicts
        if type_name == "Light lamb":
            L_lamb_dict[date] = data
        if type_name == "Medium trade lamb":
            M_T_lamb_dict[date] = data
        if type_name == "Heavy trade lamb":
            H_T_lamb_dict[date] = data
        if type_name == "Heavy lamb":
            H_lamb_dict[date] = data

dict_list = [L_lamb_dict, M_T_lamb_dict, H_T_lamb_dict, H_lamb_dict]
id_list = [L_lamb_id, M_T_lamb_id, H_T_lamb_id, H_lamb_id]

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
