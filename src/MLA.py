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
Base_URL = "http://statistics.mla.com.au/ReportApi/RunReport"

# print a formatted string of the Python JSON object
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def dict_print(data_dict):
    for key,value in data_dict.items():
        print(key, value)

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

#get dictionary of all report names and their Guids
Guid_dict = get_report_dict()


#-----------------------------------------------------------------------------#
def get_EYCI_ESTLI_data():
    #get report details from MLA API
    report_name = "Australia - EYCI and ESTLI - Daily"

    #set date range to upload, starting from current day
    DATE_RANGE = 37

    #get the return value xml text from the API
    query_string = get_query_string(DATE_RANGE, Guid_dict[report_name])
    response = requests.get(Base_URL + query_string)
    return_value = response.json()['ReturnValue']

    #make element tree from xml string
    root = ET.fromstring(return_value)
    EYCI_dict = {}
    ESTLI_dict = {}

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
            ESTLIroot = jointroot[1]
            EYCIroot = jointroot[0]
            # attribute will be of None type if no info is present
            if (type(EYCIroot.attrib.get('ConvertedData')) == str):
                EYCI_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = EYCIroot.attrib.get('ConvertedData')
            if (type(ESTLIroot.attrib.get('ConvertedData')) == str):
                ESTLI_dict[child.attrib.get('CalendarDate').replace('T', ' ')] = ESTLIroot.attrib.get('ConvertedData')
    except Exception as e:
        print("no data entries")
        exit()

    dict_print(EYCI_dict)
    dict_print(ESTLI_dict)
    return (EYCI_dict, ESTLI_dict)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def get_OTH_Sheep_data():
    report_name = "Australia - OTH lamb indicators - National - Weekly"
    DATE_RANGE = 29 #29 as report is weekly

    query_string = get_query_string(DATE_RANGE, Guid_dict[report_name])
    response = requests.get(Base_URL + query_string)
    return_value = response.json()['ReturnValue']

    L_lamb_dict = dict()
    M_T_lamb_dict = dict()
    H_T_lamb_dict = dict()
    H_lamb_dict = dict()

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

    return [L_lamb_dict, M_T_lamb_dict, H_T_lamb_dict, H_lamb_dict]

#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def get_Cattle_data():
    report_name = "Australia - Live export cattle prices - Weekly"

    #set date range to upload, starting from current day
    DATE_RANGE = 29 #29 as report is weekly

    query_string = get_query_string(DATE_RANGE, Guid_dict[report_name])
    response = requests.get(Base_URL + query_string)
    return_value = response.json()['ReturnValue']

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
    return [D_heifers_dict, D_steers_dict, T_heifers_dict, T_steers_dict]
