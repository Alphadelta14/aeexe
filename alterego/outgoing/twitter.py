
import requests
from requests_oauthlib import OAuth1

from alterego.config import config_register

config_register('twitter', {
    'app_key': '',
    'app_secret': '',
    'oauth_token': '',
    'oauth_secret': '',
})


class Twitter(object):
    def __init__(self, config):
        self._config = config
        self.config = config['twitter']

    def _auth(self):
        return OAuth1(self.config['app_key'], self.config['app_secret'],
                      self.config['oauth_token'], self.config['oauth_secret'])

    def post(self, url, params):
        return requests.post(url, data=params, auth=self._auth())

    def tweet(self, status):
        self.post('https://api.twitter.com/1.1/statuses/update.json', {
            'status': status
        }).raise_for_status()
