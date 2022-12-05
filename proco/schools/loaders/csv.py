import codecs
import csv
from typing import Dict, Iterable


def load_file(csvfile) -> Iterable[Dict]:
    csvfile.seek(0)
    reader = csv.DictReader(codecs.iterdecode(csvfile, 'utf-8-sig', errors='ignore'))
    return reader
