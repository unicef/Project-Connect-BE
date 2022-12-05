import os
import uuid


def get_imported_file_path(instance, filename):
    filename_stripped = os.path.splitext(filename)[0].split('/')[-1]
    extension = os.path.splitext(filename)[1]
    random_prefix = uuid.uuid4()
    return f'imported/{random_prefix}/{filename_stripped}{extension}'
