
import requests
from requests_oauthlib import OAuth1

from alterego.config import config_register

config_register('twitter', {
    'app_key': '',
    'app_secret': '',
    'oauth_token': '',
    'oauth_secret': '',
    'timeline_count[int]': '180',
})

config_register('feeds', {
    'state-driver': 'redis',
    'db[int]': '1',
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

    def get(self, url, params):
        return requests.get(url, params=params, auth=self._auth())

    def tweet(self, status):
        self.post('https://api.twitter.com/1.1/statuses/update.json', {
            'status': status
        }).raise_for_status()

    def home(self):
        """Read the home timeline
        """
        state = self._config.state_driver('feeds')
        last_since = int(state.get('since') or 0)
        params = {
            'count': self.config['timeline_count'],
        }
        if last_since:
            params['since_id'] = last_since
        resp = self.get('https://api.twitter.com/1.1/statuses/home_timeline.json', params)
        resp.raise_for_status()
        entries = resp.json()
        try:
            for entry in entries[::-1]:
                entities = entry.get('entities', {})
                if len(entities.get('urls', [])):
                    continue
                if len(entities.get('media', [])):
                    continue
                text = entry.get('text')
                if not text:
                    continue
                yield text.replace('\n', ' ')
                last_since = max(last_since, entry.get('id', 0))
                print(last_since, entry.get('id'))
        finally:
            state.set('since', last_since)
