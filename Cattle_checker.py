from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import os
from src.MLA import *

D_steers_id = "152f2e2a-ff0a-41d9-ad0e-61f3b25e0248"
D_heifers_id = "39b611f2-0e28-4eac-a2a8-da38f9100894"
T_steers_id = "673e043d-8921-4879-a500-4463d57f2767"
T_heifers_id = "61f7f692-8c4e-4abd-a365-4a8d08efd79f"

dict_list = get_Cattle_data()
id_list = [D_heifers_id, D_steers_id, T_heifers_id, T_steers_id]

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
