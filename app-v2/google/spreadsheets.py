from google.service import Service


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

