
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

    def timeline(self, username=None):
        """Reads a timeline

        Parameters
        ----------
        username : str
            User handle without the @. If None (default), will show the home

        Returns
        -------
        tweet_texts : list(str)
        """
        state = self._config.state_driver('feeds')
        params = {
            'count': self.config['timeline_count'],
        }
        if username is None:
            url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
            since_key = 'since'
        else:
            url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
            since_key = 'since:@{username}'.format(username=username)
            params['screen_name'] = username
        last_since = int(state.get(since_key) or 0)
        if last_since:
            params['since_id'] = last_since
        resp = self.get(url, params)
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
            state.set(since_key, last_since)
