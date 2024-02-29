from google.authenticator import Authenticator, Config as AuthenticatorConfig
from google.drive import Drive
from google.spreadsheets import Spreadsheets
from util.json import dump_json
from util.ods import ODS
from dataset.bal import Bal
import os


def main(config):
  app = App(config)
  # app.list_and_load()
  app.groom_spreadsheet('./data/__confidential/HACC.ods')


class App:
  def __init__(self, config):
    self.services = Services(config)

  def groom_spreadsheet(self, file_path=None):
    ods = ODS.load_doc(file_path=file_path)

    bal = Bal.load_sheet(ods)
    bal = bal.drop_empty()
    bal = bal.add_acct()

    ods = ODS.new_doc()
    bal.update_sheet(ods)

    file_name, ext = os.path.splitext(file_path)
    groomed_file_path = f'{file_name}-groomed{ext}'
    ods.save_doc(file_path=groomed_file_path)


  def list_and_load(self):
    print(dump_json(list(self.services.drive.list(mime_type=Drive.mime_spreadsheet))))
    """
    [
      {
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "id": "1-GauF_mzEDPA_vz7Y2fXzWW8TBadrzW9n4rJ6RaTsh4",
        "name": "HACC"
      }
    ]
    """

    # print(dump_json(self.services.spreadsheets.load(spreadsheet_id='1-GauF_mzEDPA_vz7Y2fXzWW8TBadrzW9n4rJ6RaTsh4')))
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

    # print(dump_json(self.services.spreadsheets.load_values(
    #   spreadsheet_id='1-GauF_mzEDPA_vz7Y2fXzWW8TBadrzW9n4rJ6RaTsh4',
    #   values_range='BAL')))
    """
    [
      [ "DT", "AMNT", "NOTE" ],
      [ "2/23", "50.32", "food.kauf" ],
      [ "2/18", "19.52", "SVOD" ],
      ...
    ]
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
