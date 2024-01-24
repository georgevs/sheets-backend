from services import Authenticator, Config, CachedSpreadsheets, Drive, Spreadsheets
from util_json import dump_json
import itertools
import pandas as pd

def main(config):
  authenticator = Authenticator(config)
  drive = Drive(authenticator)
  spreadsheets = CachedSpreadsheets(authenticator, config.cache_path)

  # create_spreadsheet(spreadsheets)

  # list_spreadsheet_files(drive)
  
  values = spreadsheets.load_values(spreadsheet_id='1EwmYvXtwV63K___xZmjMXg8O_msnlHU5KTHUSkGblNc', values_range='BAL')
  # println(dump_json(values))

  # update_sheet_values(spreadsheets)
  # list_sheet_values(CachedSpreadsheets(authenticator, config.cache_path))


def load_spreadsheet_values(spreadsheets, values_range):
  spreadsheet_id, values_range = '1O1TGImpeMAg9ucuohppK-dKq5EYWpm2GfRxcHy7pfho', 'BAL'
  spreadsheets.load_values(spreadsheet_id, values_range='BAL')


def update_sheet_values(spreadsheets):
  spreadsheet_id = '1O1TGImpeMAg9ucuohppK-dKq5EYWpm2GfRxcHy7pfho'
  values = [['DT', 'AMNT', 'GCASH', 'U3947', 'U9271', 'VCASH', 'VLOAN', 'NOTE']]
  values_range = 'A1:H1'
  print (
    spreadsheets.service().spreadsheets()
    .values().update(
      spreadsheetId=spreadsheet_id, 
      range=values_range, 
      valueInputOption='RAW', 
      body={'values': values})
    .execute()
  )


def create_spreadsheet(spreadsheets):
  spreadsheet_id = spreadsheets.create('hacc')
  println(spreadsheet_id)


def list_spreadsheet_files(drive):
  sheet_files = drive.list(mime_type=drive.mime_spreadsheet)
  println(dump_json(sheet_files))


def list_sheet_values(spreadsheets):
  spreadsheet_id, values_range = '1EwmYvXtwV63K___xZmjMXg8O_msnlHU5KTHUSkGblNc', 'BAL'
  spreadsheet = spreadsheets.load(spreadsheet_id)
  println(spreadsheet)
  values = spreadsheets.load_values(spreadsheet_id, values_range)
  println(list(itertools.islice(values, 10)))


def println(*args, **kwargs):
  # kwargs.setdefault('end', '\n---\n')
  print(*args, **kwargs)


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--user-name', type=str)
  parser.add_argument('--force-authenticate', action='store_true')
  parser.add_argument('--force-invalidate-cache', action='store_true')
  parser.add_argument('--secrets-path', type=str)
  parser.add_argument('--cache-path', type=str)
  parser.add_argument('--bind-addr', type=str)
  args = parser.parse_args()

  config = Config(args)

  main(config)
