from dataset.bal import Bal
from google.authenticator import Authenticator, Config as AuthenticatorConfig
from google.drive import Drive
from google.spreadsheets import Spreadsheets
from services.local_storage import LocalStorage, Config as LocalStorageConfig
from util.json import dump_json
from util.ods import ODS
from dataset.dataset import DS


def main(config, args):
  app = App(config)
  spreadsheet_name = args.spreadsheet_name or 'HACC-groomed'
  print(dump_json(app.upload_spreadsheet(spreadsheet_name=spreadsheet_name)))


class App:
  def __init__(self, config):
    self.services = Services(config)

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

    # TODO:
    categories = [
      ['borica','expense,utilities'],
      ['c1080','income'],
      ['carpool','expense'],
      ['electro','expense,utilities'],
      ['entertainment','expense'],
      ['eyecare','expense,medical'],
      ['fee','expense'],
      ['fitness','expense,sport'],
      ['food','expense'],
      ['games','expense'],
      ['groom','expense'],
      ['gviva','expense,utilities'],
      ['gvsm','expense,medical'],
      ['home','expense'],
      ['iceskating','expense,sport'],
      ['leisure','expense'],
      ['metro','expense,utilities'],
      ['office','expense'],
      ['pens','income'],
      ['pztax','expense,utilities'],
      ['sbst','expense,utilities'],
      ['sftax','expense,utilities'],
      ['shoa','expense,utilities'],
      ['ski','expense,sport'],
      ['socj','expense,utilities'],
      ['socp','income'],
      ['sport','expense,sport'],
      ['svod','expense,utilities'],
      ['telk','expense,medical'],
      ['toplo','expense,utilities'],
      ['unknown','expense'],
      ['vgsa','expense'],
      ['vgsm','expense,medical'],
      ['vviva','expense,utilities'],
    ]

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
              range=f'CATX!A2:B{len(categories) + 1}',
              majorDimension='ROWS',
              values=categories,
            ),
          ]
        )
      )
      .execute()
    )

    return result


class Services:
  def __init__(self, config):
    self.authenticator = Authenticator(config.authenticator)
    self.drive = Drive(self.authenticator)
    self.spreadsheets = Spreadsheets(self.authenticator)
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
