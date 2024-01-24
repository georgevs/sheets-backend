from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import time


build_service = build


def authenticate(client_config, scopes, bind_addr):
  flow = InstalledAppFlow.from_client_config(client_config, scopes)
  while True:
    try:
      # localhost server is not accessible from outside,
      # unless `bind_addr` is set to interface ip
      return flow.run_local_server(bind_addr=bind_addr, host='localhost', port=8080, open_browser=False, prompt='consent')
    except Exception as e:
      # the server lingers for at least a minute...
      print('exception', e.args)
      time.sleep(5)


def credentials_to_json(credentials):
  return json.loads(credentials.to_json())


def credentials_from_json(credentials):
  return Credentials.from_authorized_user_info(credentials) if credentials else None
