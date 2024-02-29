from util.os import scandir
import os


class Config:
  def __init__(self, args):
    self.data_path = args.data_path or './data'


class LocalStorage:
  def __init__(self, config):
    self.config = config

  def list(self):
    for file_path in scandir(self.config.data_path):
      id = os.path.relpath(file_path, self.config.data_path)
      yield dict(id=id, uri=file_path)

  def put(self, id, data):
    file_path = os.path.join(self.config.data_path, id)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'bw') as file:
      file.write(data)
    return dict(id=id, uri=file_path)

  def get(self, uri):
    with open(uri, 'br') as file:
      return file.read()
