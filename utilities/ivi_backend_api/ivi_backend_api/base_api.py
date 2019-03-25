import logging
from requests import Session
from json.decoder import JSONDecodeError


class BaseApi:

    def __init__(self, session: Session, host):
        self.session = session
        self.host = host
        self.log = logging.getLogger(__name__)

    def _delete(self, url, **kwargs):
        callback = self.session.delete
        return self._send(url, callback, 'DELETE', **kwargs)

    def _put(self, url, **kwargs):
        callback = self.session.put
        return self._send(url, callback, 'PUT', **kwargs)

    def _get(self, url, **kwargs):
        callback = self.session.get
        return self._send(url, callback, 'GET', **kwargs)

    def _post(self, url, **kwargs):
        callback = self.session.post
        return self._send(url, callback, 'POST', **kwargs)

    def _send(self, url, callback, method, **kwargs):
        log_msg = 'Sending {} request to {}'.format(method, url)

        log_msg = '{} and auth {}'.format(log_msg, self.session.auth)
        json_data = kwargs.get("json")
        if json_data is not None:
            log_msg = "{} and body {}".format(log_msg, json_data)
        self.log.debug(log_msg)
        response = callback(self.get_path(url), **kwargs)
        response.raise_for_status()
        self.log.debug('Response: %s' % response.text)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text

    def get_path(self, url):
        return "{}/{}".format(self.host, url)
