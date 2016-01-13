import requests
from bkpm.cli import excs


def api(f):
    def decorated(*args, **kwargs):
        resp = f(*args, **kwargs)
        if resp.status_code == 404:
            raise excs.ModelNotFoundException
        elif resp.status_code == 409:
            raise excs.ModelConflictException
        elif resp.status_code == 401:
            raise excs.AuthenticationException
        elif resp.status_code == 200:
            return resp
        else:
            raise Exception('Unexpected response code {}'.format(resp.status_code))
    return decorated


class API():
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def _headers(self):
        if self.token is None:
            raise excs.MissingAuthException
        return {
            'Authentication-Token': self.token
        }

    def _model(self, name, version=None):
        url = '{}/models/{}'.format(self.host, name)
        if version not in ['all', 'latest', None]:
            url = '{}/{}'.format(url, version)
        return url

    @api
    def register(self, name):
        return requests.post('{}/models/register'.format(self.host),
                             json={'name':name},
                             headers=self._headers())

    @api
    def delete(self, name, version):
        return requests.delete(self._model(name, version), headers=self._headers())

    @api
    def publish(self, meta_data, model_data):
        name = meta_data['name']
        return requests.post(self._model(name),
                             headers=self._headers(),
                             json={'meta': meta_data, 'model': model_data})

    @api
    def get_archive(self, name, version):
        return requests.get(self._model(name, version))

    @api
    def search(self, query):
        return requests.post('{}/models/search'.format(self.host),
                             json={'query':query})

    @api
    def get_meta(self, name):
        return requests.get('{}.json'.format(self._model(name)))
