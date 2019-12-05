
'''
UNFINISHED - couldn't find the "Australia - Retail meat prices - Quarterly"
report from the MLA API - on hold


'''

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

report_name = "Australia - Retail meat prices - Quarterly"
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

for key in Guid_dict.keys():
    print(key)

#set date range to upload, starting from current day
DATE_RANGE = 274 #274 as report is quarterly
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

beef_dict = dict()
chicken_dict = dict()
lamb_dict = dict()

beef_id = "e31c6f0f-d29b-47f9-994c-48303c72286e"
chicken_id = "dbb8fddb-24a2-406c-9fa8-c3ceb85a109c"
lamb_id = "cd22385a-8ccc-4566-add5-cf287e7ee0c4"


#make element tree from xml string
root = ET.fromstring(return_value)
calroot = root

#get calendar date collection node
for i in range(4):
    calroot = calroot[0]
    print(calroot.tag)

# for child in calroot:
#     collection_node = child
#     date = child.attrib.get('CalendarWeek').replace('T', ' ')
#     print(date)
#     #access node with required data
#     for i in range(3):
#         collection_node = collection_node[0]
#     #reached nodes of orign cities
#     for sheep_type in collection_node:
#         type_name = sheep_type.get('AttributeName3')
#         data = sheep_type[0][0].get('ConvertedData')
#
#         # attribute will be of None type if no info is present
#         if (type(data) != str):
#             continue
#
#         #put the data into the corresponding dicts
#         if type_name == "Light lamb":
#             L_lamb_dict[date] = data
#         if type_name == "Medium trade lamb":
#             M_T_lamb_dict[date] = data
#         if type_name == "Heavy trade lamb":
#             H_T_lamb_dict[date] = data
#         if type_name == "Heavy lamb":
#             H_lamb_dict[date] = data
#
# dict_list = [beef_dict, chicken_dict, lamb_dict]
# id_list = [beef_id, chicken_id, lamb_id]
#
# #upload data to amphora data website
# configuration = Configuration()
# auth_api = amphora_client.AuthenticationApi(amphora_client.ApiClient(configuration))
# token_request = amphora_client.TokenRequest(username=os.getenv('username'), password=os.getenv('password') )
#
# try:
#     # Gets a token
#     res = auth_api.authentication_request_token(token_request = token_request)
#     configuration.api_key["Authorization"] = "Bearer " + res
#     # create an instance of the Users API, now with Bearer token
#     users_api = amphora_client.UsersApi(amphora_client.ApiClient(configuration))
#     me = users_api.users_read_self()
#     print(me)
# except ApiException as e:
#     print("Exception when calling AuthenticationAPI: %s\n" % e)
#
# amphora_api = amphora_client.AmphoraeApi(amphora_client.ApiClient(configuration))
#
#
# for i in range(len(dict_list)):
#     signals = []
#     try:
#         for key,value in dict_list[i].items():
#             s = {'t': key, 'price': float(value)}
#             signals.append(s)
#         print(signals)
#         #amphora_api.amphorae_upload_signal_batch(id_list[i], request_body = signals)
#     except ApiException as e:
#         print("Exception when calling AmphoraeApi: %s\n" % e)
