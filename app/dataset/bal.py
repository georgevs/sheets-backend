from dataset.dataset import DS
from dataset.fn import group_by, list_insert, lookup_key_for_val
from util.ods import ODS


class Bal(DS):
  def load_sheet(ods, sheet_name='BAL'):
    sheet_columns = ['DT', 'AMNT', 'ACCT', 'GCASH', 'U3947', 'U9271', 'VCASH', 'VLOAN', 'NOTE']
    cols, rows = ods.load_sheet(sheet_name, sheet_columns)
    return Bal(sheet_name, cols, rows)
  
  def __init__(self, sheet_name, cols, rows):
    super().__init__(cols, rows)
    self.sheet_name = sheet_name
    self.note = self.col('NOTE')

  def update_sheet(self, ods, *, sheet_name=None, index=0):
    sheet=ODS.sheet_for(sheet_name or self.sheet_name, self.cols(), self.rows())
    ods.update_sheet(sheet=sheet, index=index)

  def notes(self):
    return (
      filter(bool,
        map(self.note, self.rows())))

  def accts_index(self):
    return (
      map(
        lambda x: (x[0], set(x[1])),
        group_by(Bal.acct_from_note, self.notes())))

  def acct_from_note(val):
    acct = lookup_key_for_val(Bal.lookup_notes, val.lower().strip())
    if not acct:
      acct = val.lower().strip().partition(' ')[0].partition('.')[0]
      acct = lookup_key_for_val(Bal.lookup_accts, acct, acct)
    return acct

  def init(config):
    Bal.lookup_notes = config.get('lookup_notes', {})
    Bal.lookup_accts = config.get('lookup_accts', {})
    Bal.whitelist_accts = config.get('whitelist_accts', None)

  lookup_notes = None
  lookup_accts = None
  whitelist_accts = None

  def drop_empty(self):
    return Bal(self.sheet_name, *self.filter(fn=self.note))
  
  def copy_only_columns(self, cols):  
    return Bal(self.sheet_name, *self.filter(cols=cols))

  def add_acct(self):
    if self.cols_index.get('ACCT'):
      return self
    cols = self.cols()
    pos = 2
    assert pos <= len(cols)
    cols.insert(pos, 'ACCT')
    rows = map(lambda row: list_insert(row.copy(), pos, Bal.acct_from_note(self.note(row))), self.rows())
    if Bal.whitelist_accts:
      rows = filter(lambda row: row[pos] in Bal.whitelist_accts, rows)
    return Bal(self.sheet_name, cols, rows)
