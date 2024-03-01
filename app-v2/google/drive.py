from google.service import Service


# https://developers.google.com/drive/api/reference/rest
class Drive(Service):
  def __init__(self, authenticator):
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    super().__init__(authenticator, 'drive', 'v3', scopes)

  def list(self, mime_type=None):
    mime_type = mime_type and Drive.mime_types[mime_type]
    query = {'q': f"mimeType='{mime_type}'"} if mime_type else {}
    return (
      self.service()
      .files().list(**query)
      .execute()['files']
    )
  
  def export(self, file_id, mime_type):
    mime_type = Drive.mime_types[mime_type]
    return (
      self.service()
      .files().export(fileId=file_id, mimeType=mime_type)
      .execute()
    )
  
  mime_ods = 'application/x-vnd.oasis.opendocument.spreadsheet'
  mime_spreadsheet = 'application/vnd.google-apps.spreadsheet'
  mime_types = {
    mime_ods: mime_ods,
    mime_spreadsheet: mime_spreadsheet,
  }
