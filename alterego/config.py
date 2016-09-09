
import six
from six.moves.configparser import ConfigParser

__all__ = ['Configuration', 'config_register']

BOOL_MAP = {
    True: ['true', 'yes', 'y', '1'],
    False: ['false', 'no', 'n', '0'],
}


class Configuration(object):
    defaults = {}

    def __init__(self, filename=None):
        self._config = ConfigParser()
        self._set_defaults()
        self._state_driver = None
        if filename is not None:
            self.load(filename)

    def _set_defaults(self):
        """Set defaults for config
        """
        self._config.add_section('main')
        for key, value in six.iteritems(self.defaults):
            if isinstance(value, dict):
                self._config.add_section(key)
                for subkey, subvalue in six.iteritems(value):
                    self._config.set(key, subkey, subvalue)
            else:
                self._config.set('main', key, value)

    def load(self, filename):
        """Load the configuration by filename
        """
        self._config.read(filename)

    def save(self, filename):
        """Save the configuration to a file
        """
        with open(filename, 'w') as handle:
            self._config.write(handle)

    @staticmethod
    def sanitize(items):
        options = {}
        for key, value in items:
            if key.endswith('[int]'):
                options[key[:-5]] = int(value)
            elif key.endswith('[bool]'):
                value = value.lower()
                if value in BOOL_MAP[True]:
                    value = True
                elif value in BOOL_MAP[False]:
                    value = False
                else:
                    raise ValueError('Expected boolean for {}'.format(key))
                options[key[:-6]] = value
            else:
                options[key] = value
        return options

    def __getitem__(self, name):
        if self._config.has_section(name):
            return self.sanitize(self._config.items(name))
        elif name == 'main':
            raise ValueError('Missing main section of configuration')
        return self['main'][name]

    def state_driver(self):
        """Get an instance of the state driver
        """
        from database import state

        if self._state_driver is None:
            if self['state-driver'] == 'redis':
                self._state_driver = state.RedisDriver(self)
            elif self['state-driver'] == 'dict':
                self._state_driver = state.MemoryDriver(self)
            else:
                raise ValueError('Unknown state driver')
        return self._state_driver


def config_register(name, default=None):
    Configuration.defaults[name] = default
