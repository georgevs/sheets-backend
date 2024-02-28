from google.authenticator import Authenticator, Config as AuthenticatorConfig
from google.drive import Drive
from google.spreadsheets import Spreadsheets
from util.json import dump_json


def main(config):
  services = Services(config)

  # print(list(services.drive.list(mime_type=Drive.mime_spreadsheet)))
  
  print(dump_json(services.spreadsheets.load(spreadsheet_id='1-GauF_mzEDPA_vz7Y2fXzWW8TBadrzW9n4rJ6RaTsh4')))
  """
  {
    "spreadsheetId": "1-GauF_mzEDPA_vz7Y2fXzWW8TBadrzW9n4rJ6RaTsh4",
    "properties": {
      "title": "HACC",
      ...
    },
    "sheets": [
      {
        "properties": {
          "sheetId": 0,
          "title": "BAL",
          "index": 0,
          "sheetType": "GRID",
          "gridProperties": {
            "rowCount": 1899,
            "columnCount": 27,
            "frozenRowCount": 2
          }
        }
      },
      {
        "properties": {
          "sheetId": 1430381537,
          "title": "ACCTS",
          "index": 1,
          "sheetType": "GRID",
          "gridProperties": {
            "rowCount": 1001,
            "columnCount": 125,
            "frozenRowCount": 1,
            "frozenColumnCount": 1
          }
        }
        ...
      ]
    },
  }
  """


class Services:
  def __init__(self, config):
    self.authenticator = Authenticator(config.authenticator)
    self.drive = Drive(self.authenticator)
    self.spreadsheets = Spreadsheets(self.authenticator)


class Config:
  def __init__(self, args):
    self.authenticator = AuthenticatorConfig(args)


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--bind-addr', type=str)
  parser.add_argument('--secrets-path', type=str)
  args = parser.parse_args()

  config = Config(args)

  main(config)
