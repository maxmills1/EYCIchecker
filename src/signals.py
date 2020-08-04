import sys
from amphora.client import AmphoraDataRepositoryClient

# upload cattle signals
def upload_signals_multiple_amphorae(client: AmphoraDataRepositoryClient, signals_dict_list, id_list):
    for i in range(len(signals_dict_list)):
        amphora_id = id_list[i]
        success_indicator = upload_MLA_signals(client, signals_dict_list[i], amphora_id)

################################################################################
def upload_MLA_signals(client: AmphoraDataRepositoryClient, signals_dict, amphora_id):
    signals = []
    success_indicator = 0
    try:
        for key,value in signals_dict.items():
            s = {'t': key, 'price': float(value)}
            signals.append(s)

        amphora = client.get_amphora(amphora_id)
        if len(signals) > 1:
            print(f'Uploading signals to {amphora.metadata.name} {amphora.metadata.id}')
            print(f'Properties of first signal val: {signals[0].keys()}')
            amphora.push_signals_dict_array(signals) # this sends the data to Amphora Data
            print(f'Sent {len(signals)} signals')
        else:
            print(f'0 signals for {amphora.metadata.name}')

    except Exception as e:
        print("Exception: %s\n" % e)
        success_indicator = 0
        raise e
    return success_indicator

def push_signal_to_amphora(signal, amphora):

    sep = ':'
    print(sep.join(['Pushing signal for Amphora for', amphora.metadata.name]))
    print(signal)

    success_indicator = 0

    try:
        amphora.push_signals_dict_array(signal)
        success_indicator = 1
    except:
        success_indicator = 0

    return success_indicator
