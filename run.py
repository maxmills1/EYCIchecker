from dotenv import load_dotenv
load_dotenv()
from amphora.client import AmphoraDataRepositoryClient, Credentials
import os
import src.MLA as funcs
from src.signals import push_signal_to_amphora
import json
import time

#logging: potentially more to add
start = time.time()

#LOAD AMPHORAE IDS
amphora_ids_file_name = os.getenv('amphora_ids_file_name')
with open(amphora_ids_file_name, 'r') as file:
    d_string = file.read()
    amphora_ids = json.loads(d_string)

#upload data to amphora data website
credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials)


#TODO: should update to most recent timestamp rather than all values in the future
#DAILY REPORTS
#upload eyci, estli data, return value in form {'eyci': eyci_signals, ...}
eyci_estli_data = funcs.get_eyci_estli_data()
for report,signals in eyci_estli_data.items():
    amphora = client.get_amphora(amphora_ids[report])
    success_indicator = push_signal_to_amphora(signals, amphora)

#WEEKLY REPORTS
#upload cattle data, return value in form {data_name: signals, ...}
cattle_data = funcs.get_cattle_data()
for report,signals in cattle_data.items():
    amphora = client.get_amphora(amphora_ids[report])
    success_indicator = push_signal_to_amphora(signals, amphora)

#upload OTH sheep data
oth_sheep_data = funcs.get_oth_sheep_data()
for report,signals in cattle_data.items():
    amphora = client.get_amphora(amphora_ids[report])
    success_indicator = push_signal_to_amphora(signals, amphora)

end = time.time()
print('time to complete: ' + str(end-start))

################################################################################
