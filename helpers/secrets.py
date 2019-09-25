import yaml
import dotmap

with open('secrets.yaml') as s_file:
    s_data = dotmap.DotMap(yaml.safe_load(s_file))
    SSO_CLIENT_ID = s_data.client_id
    SSO_SECRET_KEY = s_data.secret_key
    SSO_CALLBACK = s_data.callback
