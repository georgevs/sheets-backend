from dataset.bal import Bal
from google.authenticator import Authenticator, Config as AuthenticatorConfig
from google.drive import Drive
from google.spreadsheets import Spreadsheets
from services.local_storage import LocalStorage, Config as LocalStorageConfig
from util.json import dump_json, try_load_json
from util.ods import ODS
from dataset.dataset import DS


def main(config, args):
  app = App(config)
  spreadsheet_name = args.spreadsheet_name or 'HACC-groomed'
  print(dump_json(app.upload_spreadsheet(spreadsheet_name=spreadsheet_name)))


class App:
  def __init__(self, config):
    self.services = Services(config)
    App.categories = config.categories

  def upload_spreadsheet(self, spreadsheet_name):
    is_target_spreadsheet = (lambda it: it.get('id') == f'{spreadsheet_name}.ods')
    spreadsheet = next(filter(is_target_spreadsheet, self.services.storage.list()))
    uri = spreadsheet.get('uri')
    
    data = self.services.storage.get(uri=uri)
    ods = ODS.load_doc(data=data)
    bal = DS(*ods.load_sheet(sheet_name='BAL', sheet_columns=['DT', 'AMNT', 'ACCT']))
    del ods

    spreadsheets = self.services.drive.list(mime_type=Drive.mime_spreadsheet)
    is_target_spreadsheet = (lambda it: it.get('name') == spreadsheet_name)
    spreadsheet = next(filter(is_target_spreadsheet, spreadsheets), None)
    spreadsheet_id = spreadsheet.get('id') if spreadsheet else None
    if not spreadsheet_id:
      spreadsheet = (self.services.spreadsheets.service()
        .spreadsheets().create(
          body=dict(
            properties=dict(
              title=spreadsheet_name
            ),
            sheets=[
              dict(
                properties=dict(
                  title='BAL'
                )
              ),
              dict(
                properties=dict(
                  title='CATX'
                )
              )
            ]
          ),
          fields='spreadsheetId'
        )
        .execute()
      )
      spreadsheet_id = spreadsheet.get('spreadsheetId')

    result = (self.services.spreadsheets.service().spreadsheets()
      .values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=dict(
          valueInputOption='RAW',
          includeValuesInResponse=False,
          data=[
            dict(
              range='BAL!A1:C1',
              majorDimension='ROWS',
              values=[bal.cols()]
            ),
            dict(
              range=f'BAL!A2:C{len(bal.rows_list) + 1}',
              majorDimension='ROWS',
              values=bal.rows_list
            ),
            dict(
              range='CATX!A1:B1',
              majorDimension='ROWS',
              values=[['ACCT','CAT']]
            ),
            dict(
              range=f'CATX!A2:B{len(App.categories) + 1}',
              majorDimension='ROWS',
              values=App.categories,
            ),
          ]
        )
      )
      .execute()
    )

    return result

  categories = None


class Services:
  def __init__(self, config):
    self.authenticator = Authenticator(config.authenticator)
    self.drive = Drive(self.authenticator)
    self.spreadsheets = Spreadsheets(self.authenticator)
    self.storage = LocalStorage(config.storage)

class Config:
  def __init__(self, args):
    config = try_load_json(args.config_path) or {}
    self.authenticator = AuthenticatorConfig(args)
    self.storage = LocalStorageConfig(args)
    self.categories = config.get('categories', [])


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--bind-addr', type=str)
  parser.add_argument('--secrets-path', type=str)
  parser.add_argument('--data-path', type=str, default='./data/__confidential')
  parser.add_argument('--config-path', type=str, default='./secrets/config.json')
  parser.add_argument('--spreadsheet-name', type=str)
  args = parser.parse_args()

  config = Config(args)

  main(config, args)
