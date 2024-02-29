from dataset.fn import index_from_list, list_from_index


class DS:
  def __init__(self, cols, rows):
    self.cols_index = index_from_list(cols)
    self.rows_list = list(rows)
    
  def cols(self):
    return list_from_index(self.cols_index)  

  def rows(self):
    return iter(self.rows_list)

  def col(self, name):
    return lambda row: row[self.cols_index[name]]

  def filter(self, fn, cols=None):
    cols = cols or self.cols()
    cols_index = index_from_list(cols)
    req_cols = [col for col in cols if col in self.cols()]
    def copy(row):
      xs = len(cols)*[None]
      for col in req_cols:
        xs[cols_index[col]] = row[self.cols_index[col]]
      return xs
    return cols, map(copy, filter(fn, self.rows()))
