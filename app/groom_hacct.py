from dataset.bal import Bal
from services.local_storage import LocalStorage, Config as LocalStorageConfig
from util.json import dump_json, try_load_json
from util.ods import ODS


def main(config, args):
  app = App(config)
  print(dump_json(app.groom_hacct(
    spreadsheet_name=args.spreadsheet_name,
    spreadsheet_groomed_name=args.spreadsheet_groomed_name,
  )))
  

class App:
  def __init__(self, config):
    self.services = Services(config)
    Bal.init(dict(**config.bal, whitelist_accts=config.whitelist_accts))

  def groom_hacct(self, spreadsheet_name, spreadsheet_groomed_name):
    is_target_spreadsheet = (lambda it: it.get('id') == f'{spreadsheet_name}.ods')
    spreadsheet = next(filter(is_target_spreadsheet, self.services.storage.list()))
    spreadsheet_id, spreadsheet_uri = spreadsheet.get('id'), spreadsheet.get('uri')

    data = self.services.storage.get(uri=spreadsheet_uri)
    ods = ODS.load_doc(data=data)

    bal = Bal.load_sheet(ods)
    bal = bal.drop_empty()
    bal = bal.add_acct()

    ods = ODS.new_doc()
    bal.update_sheet(ods)
    data = ods.to_bytes_doc()

    id = spreadsheet_id.replace(spreadsheet_name, spreadsheet_groomed_name)
    return self.services.storage.put(id=id, data=data)


class Services:
  def __init__(self, config):
    self.storage = LocalStorage(config.storage)

class Config:
  def __init__(self, args):
    config = try_load_json(args.config_path) or {}
    self.storage = LocalStorageConfig(args)
    self.bal = config.get('bal', {})
    self.whitelist_accts = config.get('whitelist_accts', None)


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--data-path', type=str, default='./data/confidential')
  parser.add_argument('--config-path', type=str, default='./secrets/config.json')
  parser.add_argument('--spreadsheet-name', type=str, default='HACC')
  parser.add_argument('--spreadsheet-groomed-name', type=str, default='HACC-groomed')
  args = parser.parse_args()

  config = Config(args)

  main(config, args)
