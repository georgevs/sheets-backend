import csv
import itertools


def sample(n, xs):
  return itertools.islice(xs, n)

def lookup_key_for_val(lookup_index, val, default=None):
  for key,vals in lookup_index.items():
    if val in vals: 
      return key
  return default

def group_by(key,xs):
  return itertools.groupby(sorted(xs, key=key), key=key)

def list_insert(xs, pos, val):
  xs.insert(pos, val)
  return xs

def index_from_list(xs):
  return { n:i for i,n in enumerate(xs) }

def list_from_index(index):
  return [x[0] for x in sorted(index.items(), key=lambda x:x[1])]

def save_csv(file_path, cols, rows):
  with open(file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(cols)
    writer.writerows(rows)
