from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import os
from src.MLA import *

EYCI_id = "1bd74490-ccf6-43d1-99f1-ef53f60c293c"
ESTLI_id = "35f32a02-5abf-417b-a8ec-40dc7ac3ff7d"

EYCI_dict, ESTLI_dict = get_EYCI_ESTLI_data()

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
EYCI_signals = []
ESTLI_signals = []

try:
    for key,value in EYCI_dict.items():
        s = {'t': key, 'price': float(value)}
        EYCI_signals.append(s)
    for key,value in ESTLI_dict.items():
        s = {'t': key, 'price': float(value)}
        ESTLI_signals.append(s)

    print(EYCI_signals)
    amphora_api.amphorae_upload_signal_batch(EYCI_id, request_body = EYCI_signals)
    amphora_api.amphorae_upload_signal_batch(ESTLI_id, request_body = ESTLI_signals)
except ApiException as e:
    print("Exception when calling AmphoraeApi: %s\n" % e)
