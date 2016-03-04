"""
Jenkins API does not use persistent HTTP connections feature of request Python module

THis class extends jenkinsapi.utils.requester.Requester class and uses requests.Session()
"""

import logging
import requests

from jenkinsapi.utils.requester import Requester


class PersistentRequester(Requester):
    """
    Override get_url and post_url methods that make HTTP requests and use HTTP connections pooling
    """
    _request = None

    @property
    def request(self):
        if self._request is None:
            self._request = requests.Session()

        return self._request

    def get_url(self, url, params=None, headers=None, allow_redirects=True):
        requestKwargs = self.get_request_dict(
            params=params,
            headers=headers,
            allow_redirects=allow_redirects)
        resp = self.request.get(self._update_url_scheme(url), **requestKwargs)

        logging.info('get_url <{}>: {} ({})'.format(url, resp, resp.text))
        return resp

    def post_url(self, url, params=None, data=None, files=None,
                 headers=None, allow_redirects=True):
        requestKwargs = self.get_request_dict(
            params=params,
            data=data,
            files=files,
            headers=headers,
            allow_redirects=allow_redirects)
        resp = self.request.post(self._update_url_scheme(url), **requestKwargs)

        logging.info('post_url <{}>: {} ({})'.format(url, resp, resp.text))
        return resp
