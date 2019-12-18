from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import os
from src.MLA import *

L_lamb_id = "fdf6cc1a-c2bc-4d22-a013-f697e6e16771"
M_T_lamb_id = "f8ea22f4-b08e-46e3-abb4-8721478b9f94"
H_T_lamb_id = "5fa13614-ac5a-4af7-a908-c6f8414f4b26"
H_lamb_id = "d4975810-85e7-44e3-998f-a69438f4ea49"

dict_list = get_OTH_Sheep_data()
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
