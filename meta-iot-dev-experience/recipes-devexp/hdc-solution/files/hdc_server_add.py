import json

with open('/var/wra/files/default/default_settings', 'r+') as f:
    data = json.load(f)
    data['device_config'][0]['model_number'] = "MI-IDP-IOT-GW-EVAL"
    data['ems_server_config'][0]['server_address'] = "wrpoc6.axeda.com"
    f.seek(0)
    f.write(json.dumps(data,indent=5,sort_keys=True))
    f.truncate()
