import os
import io
import json
import tarfile
import configparser


def extract_model(data, outdir):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # extract files to disk
    tar = tarfile.open(fileobj=io.BytesIO(data))

    # to temporary location, to pull out necessary metadata
    tar.extractall('/tmp/')
    with open('/tmp/meta.json', 'r') as f:
        meta = json.load(f)
    version, name = meta['version'], meta['name']
    path = os.path.join(outdir, name, version)
    if not os.path.isdir(path):
        os.makedirs(path)
    os.rename('/tmp/meta.json', os.path.join(path, 'meta.json'))
    os.rename('/tmp/model.json', os.path.join(path, 'model.json'))
    return version


def load_config(path, registry='default'):
    cparser = configparser.ConfigParser()
    cparser.read(path)
    config = cparser[registry]
    return config


def save_config(path, registry, **data):
    cparser = configparser.ConfigParser()
    cparser.read(path)
    cparser[registry].update(data)
    with open(path, 'w') as f:
        cparser.write(f)
