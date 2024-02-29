from google.authenticator import Authenticator, Config as AuthenticatorConfig
from google.drive import Drive
from util.json import dump_json
from services.local_storage import LocalStorage, Config as LocalStorageConfig


def main(config, args):
  app = App(config)
  spreadsheet_name = args.spreadsheet_name or 'HACC'
  print(dump_json(app.download_spreadsheet(spreadsheet_name=spreadsheet_name)))


class App:
  def __init__(self, config):
    self.services = Services(config)

  def download_spreadsheet(self, spreadsheet_name):
    spreadsheets = self.services.drive.list(mime_type=Drive.mime_spreadsheet)
    is_target_spreadsheet = (lambda it: it.get('name') == spreadsheet_name)
    spreadsheet = next(filter(is_target_spreadsheet, spreadsheets))
    spreadsheet_id = spreadsheet.get('id')
    data = self.services.drive.export(file_id=spreadsheet_id, mime_type=Drive.mime_ods)
    id = f'{spreadsheet_name}.ods'
    uri = self.services.storage.put(id, data=data)
    return dict(id=id, uri=uri)


class Services:
  def __init__(self, config):
    self.authenticator = Authenticator(config.authenticator)
    self.drive = Drive(self.authenticator)
    self.storage = LocalStorage(config.storage)

class Config:
  def __init__(self, args):
    self.authenticator = AuthenticatorConfig(args)
    self.storage = LocalStorageConfig(args)


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--bind-addr', type=str)
  parser.add_argument('--secrets-path', type=str)
  parser.add_argument('--data-path', type=str, default='./data/__confidential')
  parser.add_argument('--spreadsheet-name', type=str)
  args = parser.parse_args()

  config = Config(args)

  main(config, args)
