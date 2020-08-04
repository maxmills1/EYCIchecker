from dotenv import load_dotenv
load_dotenv()
import requests
import json
from xml.dom import minidom
from xml.dom.minidom import Document
import xml.etree.ElementTree as ET
import time
import datetime
import os

#base URL for queries to the MLA API
base_url = "http://statistics.mla.com.au/ReportApi/RunReport"

# print a formatted string of the Python JSON object
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

#turn date to string formatted so that the MLA API accepts
def d_to_string(d):
    datestring = '{:02d}'.format(d.day) + '%2F' + '{:02d}'.format(d.month) + '%2F' + '{:02d}'.format(d.year)
    return datestring

def get_report_dict():
    response = requests.get("http://statistics.mla.com.au/ReportApi/GetReportList")
    #check that the get request worked
    if response.status_code != 200:
        print("Exception when accessing MLA website")
    else:
        print("MLA website access successful")
    report_details = response.json()['ReturnValue']
    report_dict = {}
    for report in report_details:
        report_dict[report['Name']] = report["ReportGuid"]
    return report_dict

def get_query_string(range, guid):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=range)
    return "?ReportGuid=" + guid + "&FromDate=" + \
        d_to_string(start_date) + "&ToDate=" + d_to_string(today)

#formats the date: signal structure of mla data to a format recognisable by amphora
def mla_dict_to_signals(signals_dict):
    signals = []
    for key,value in signals_dict.items():
        s = {'t': key, 'price': float(value)}
        signals.append(s)
    return signals

#-----------------------------------------------------------------------------#
def get_eyci_estli_data():
    Guid_dict = get_report_dict()
    #get report details from MLA API
    report_name = "Australia - EYCI and ESTLI - Daily"
    date_range = int(os.getenv('daily_date_range')) #number of days to search over

    #get the return value xml text from the API
    query_string = get_query_string(date_range, Guid_dict[report_name])
    response = requests.get(base_url + query_string)
    return_value = response.json()['ReturnValue']

    #make element tree from xml string
    root = ET.fromstring(return_value)
    eyci_dict = {}
    estli_dict = {}

    try:
        #get calendar date collection node
        calroot = root
        for i in range(4):
            calroot = calroot[0]
        for child in calroot:
            jointroot = child
            #access node with required data
            for i in range(3):
                jointroot = jointroot[0]
            estliroot = jointroot[1]
            eyciroot = jointroot[0]
            # attribute will be of None type if no info is present
            if (type(eyciroot.attrib.get('ConvertedData')) == str):
                eyci_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = eyciroot.attrib.get('ConvertedData')
            if (type(estliroot.attrib.get('ConvertedData')) == str):
                estli_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = estliroot.attrib.get('ConvertedData')
    except Exception as e:
        print("no data entries for eyci, estli")
        exit()

    #return dictionaries of {'t': date, 'price': float(value)} format
    return { 'eyci': mla_dict_to_signals(eyci_dict),
            'estli': mla_dict_to_signals(estli_dict)
            }
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def get_oth_sheep_data():
    Guid_dict = get_report_dict()
    report_name = "Australia - OTH lamb indicators - National - Weekly"
    date_range = int(os.getenv('weekly_date_range')) #number of days to search over

    query_string = get_query_string(date_range, Guid_dict[report_name])
    response = requests.get(base_url + query_string)
    return_value = response.json()['ReturnValue']

    l_lamb_dict = dict()
    m_t_lamb_dict = dict()
    h_t_lamb_dict = dict()
    h_lamb_dict = dict()

    #make element tree from xml string
    root = ET.fromstring(return_value)
    calroot = root

    #get calendar date collection node
    for i in range(4):
        calroot = calroot[0]

    for child in calroot:
        collection_node = child
        date = child.attrib.get('CalendarWeek').replace('T', ' ')
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
                l_lamb_dict[date] = data
            if type_name == "Medium trade lamb":
                m_t_lamb_dict[date] = data
            if type_name == "Heavy trade lamb":
                h_t_lamb_dict[date] = data
            if type_name == "Heavy lamb":
                h_lamb_dict[date] = data


    return {'l_lamb': mla_dict_to_signals(l_lamb_dict),
            'm_t_lamb': mla_dict_to_signals(m_t_lamb_dict),
            'h_t_lamb': mla_dict_to_signals(h_t_lamb_dict),
            'h_lamb': mla_dict_to_signals(h_lamb_dict)}

#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def get_cattle_data():
    Guid_dict = get_report_dict()
    report_name = "Australia - Live export cattle prices - Weekly"
    date_range = int(os.getenv('weekly_date_range')) #number of days to search over

    query_string = get_query_string(date_range, Guid_dict[report_name])
    response = requests.get(base_url + query_string)
    return_value = response.json()['ReturnValue']

    d_steers_dict = dict()
    d_heifers_dict = dict()
    t_steers_dict = dict()
    t_heifers_dict = dict()

    #make element tree from xml string
    root = ET.fromstring(return_value)
    calroot = root

    #get calendar date collection node
    for i in range(4):
        calroot = calroot[0]

    for child in calroot:
        collection_node = child
        date = child.attrib.get('CalendarMonth').replace('T', ' ')
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
                        d_steers_dict[date] = data
                    elif cow_type.get('AttributeName3') == "Heifer":
                        d_heifers_dict[date] = data
                elif city.get('AttributeName5') == "Townsville":
                    if cow_type.get('AttributeName3') == "Steer":
                        t_steers_dict[date] = data
                    elif cow_type.get('AttributeName3') == "Heifer":
                        t_heifers_dict[date] = data

    return {'d_heifers': mla_dict_to_signals(d_heifers_dict),
            'd_steers': mla_dict_to_signals(d_steers_dict),
            't_heifers': mla_dict_to_signals(t_heifers_dict),
            't_steers': mla_dict_to_signals(t_steers_dict)
            }

################################################################################

def get_cattle_ids(amphora_ids_file_name):
    with open(amphora_ids_file_name, 'r') as file:
        d_string = file.read()
        ids = json.loads(d_string)

    return [ids['d_heifers'], ids['d_steers'],
        ids['t_heifers'], ids['t_steers']]

################################################################################

def get_sheep_ids(amphora_ids_file_name):
    with open(amphora_ids_file_name, 'r') as file:
        d_string = file.read()
        ids = json.loads(d_string)

    return [ids['l_lamb'], ids['m_t_lamb'], ids['h_t_lamb'],
            ids['h_lamb']]

################################################################################
################################################################################

'''
#Amphorae ids:
d_heifers_id = "39b611f2-0e28-4eac-a2a8-da38f9100894"
d_steers_id = "152f2e2a-ff0a-41d9-ad0e-61f3b25e0248"
t_heifers_id = "61f7f692-8c4e-4abd-a365-4a8d08efd79f"
t_steers_id = "673e043d-8921-4879-a500-4463d57f2767"
eyci_id = "1bd74490-ccf6-43d1-99f1-ef53f60c293c"
estli_id = "35f32a02-5abf-417b-a8ec-40dc7ac3ff7d"
l_lamb_id = "fdf6cc1a-c2bc-4d22-a013-f697e6e16771"
m_t_lamb_id = "f8ea22f4-b08e-46e3-abb4-8721478b9f94"
h_t_lamb_id = "5fa13614-ac5a-4af7-a908-c6f8414f4b26"
h_lamb_id = "d4975810-85e7-44e3-998f-a69438f4ea49"

amphora_ids = {'d_heifers': d_heifers_id,
                'd_steers': d_steers_id,
                't_heifers': t_heifers_id,
                't_steers': t_steers_id,
                'eyci': eyci_id,
                'estli': estli_id,
                'l_lamb': l_lamb_id,
                'm_t_lamb': m_t_lamb_id,
                'h_t_lamb': h_t_lamb_id,
                'h_lamb': h_lamb_id
                }

amphora_ids_file_name=data/mla_amphora_ids.csv
with open(amphora_ids_file_name, 'w') as file:
    file.write(json.dumps(amphora_ids))

'''
