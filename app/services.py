from util_google import authenticate, credentials_from_json, credentials_to_json, build_service
from util_json import load_json, save_json, try_load_json
from urllib.parse import quote


class Config:
  def __init__(self, args):
    self.secrets_path = args.secrets_path or 'secrets'
    self.cache_path = args.cache_path or '__cache'
    self.bind_addr = args.bind_addr or None
    self.client_secret_file_path = f'{self.secrets_path}/client_secret.json'
    self.cached_credentials_file_path = f'{self.secrets_path}/credentials.json'


class Authenticator:
  def __init__(self, config):
    self.config = config
    self.credentials = None

  def authenticate(self, scopes):
    if not self.credentials:
      self.credentials = credentials_from_json(
          try_load_json(self.config.cached_credentials_file_path))
    if self.credentials and not set(self.credentials.scopes).issuperset(set(scopes)):
      scopes = list(set(self.credentials.scopes).union(set(scopes)))
      self.credentials = None
    if not self.credentials:
      client_config = load_json(self.config.client_secret_file_path)
      self.credentials = authenticate(client_config, scopes, bind_addr=self.config.bind_addr)
      save_json(self.config.cached_credentials_file_path,
                credentials_to_json(self.credentials))
    return self.credentials


class Service:
  def __init__(self, authenticator, name, version, scopes):
    self.authenticator = authenticator
    self.scopes = scopes
    self.name = name
    self.version = version
    self.authenticated_service = None

  def service(self):
    if not self.authenticated_service:
      credentials = self.authenticator.authenticate(self.scopes)
      self.authenticated_service = build_service(self.name, self.version, credentials=credentials)
    return self.authenticated_service


class Spreadsheets(Service):
  def __init__(self, authenticator):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    super().__init__(authenticator, 'sheets', 'v4', scopes)

  def load(self, spreadsheet_id):
    return (
      self.service().spreadsheets()
      .get(spreadsheetId=spreadsheet_id)
      .execute()
    )

  def load_values(self, spreadsheet_id, values_range):
    return (
      self.service().spreadsheets()
      .values().get(spreadsheetId=spreadsheet_id, range=values_range)
      .execute()
      .get('values')
    )
  
  def create(self, title):
    return (
      self.service().spreadsheets()
      .create(body={'properties': {'title': title}}, fields="spreadsheetId")
      .execute()
      .get('spreadsheetId')
    )


class Drive(Service):
  def __init__(self, authenticator):
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    super().__init__(authenticator, 'drive', 'v3', scopes)
    self.mime_spreadsheet = 'application/vnd.google-apps.spreadsheet'
    self.mime_types = {self.mime_spreadsheet: self.mime_spreadsheet}

  def list(self, mime_type=None):
    mime_type = mime_type and self.mime_types[mime_type]
    query = {'q': f"mimeType='{mime_type}'"} if mime_type else {}
    return self.service().files().list(**query).execute()['files']


class CachedSpreadsheets(Spreadsheets):
  def __init__(self, authenticator, cache_path):
    super().__init__(authenticator)
    self.cache_path = cache_path

  def cached_spreadsheet_file_path(self, spreadsheet_id):
    return f'{self.cache_path}/sheet-{spreadsheet_id}.json'

  def cached_sheet_values_file_path(self, spreadsheet_id, values_range):
    return f'{self.cache_path}/sheet-{spreadsheet_id}-{quote(values_range)}.json'

  def load(self, spreadsheet_id):
    cached_spreadsheet_file_path = self.cached_spreadsheet_file_path(spreadsheet_id)
    spreadsheet = try_load_json(cached_spreadsheet_file_path)
    if not spreadsheet:
      spreadsheet = super().load(spreadsheet_id)
      save_json(cached_spreadsheet_file_path, spreadsheet)
    return spreadsheet

  def load_values(self, spreadsheet_id, values_range):
    cached_sheet_values_file_path = self.cached_sheet_values_file_path(spreadsheet_id, values_range)
    values = try_load_json(cached_sheet_values_file_path)
    if not values:
      values = super().load_values(spreadsheet_id, values_range)
      save_json(cached_sheet_values_file_path, values)
    return values
