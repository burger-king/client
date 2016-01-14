import os
import json
import h5py
from sklearn.linear_model import LinearRegression


def _paths(dir):
    params_f = os.path.join(dir, 'params.h5')
    meta_f = os.path.join(dir, 'meta.json')
    return meta_f, params_f


def save(model, dir):
    """export a sklearn model to bk format"""
    meta_f, params_f = _paths(dir)

    if os.path.exists(meta_f):
        meta = json.load(open(meta_f, 'r'))
    else:
        meta = {}

    # only supports linear regression at the moment
    assert isinstance(model, LinearRegression)
    h5f = h5py.File(params_f, 'w')
    h5f.create_dataset('coef', data=model.coef_)
    h5f.create_dataset('intercept', data=model.intercept_)
    h5f.close()

    meta.update({'type': 'linear_regression'})
    json.dump(meta, open(meta_f, 'w'))


def load(dir):
    """import a bk model as a sklearn model"""
    meta_f, params_f = _paths(dir)

    meta = json.load(open(meta_f, 'r'))
    type = meta['type']

    # only supports linear regression at the moment
    assert type == 'linear_regression'
    h5f = h5py.File(params_f, 'r')
    coef = h5f['coef'][:]
    intercept = h5f['intercept'][()] # to retrieve scalar values
    h5f.close()

    model = LinearRegression()
    model.coef_ = coef
    model.intercept_ = intercept
    return model