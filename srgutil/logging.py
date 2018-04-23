# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


import logging.config
from srgutil.interfaces import IMozLogging


class Logging(IMozLogging):
    _log_config = {
        # Note that the formatters.json.logger_name must match
        # loggers.<logger_name> key
        'version': 1,
        'formatters': {
            'json': {
                '()': 'dockerflow.logging.JsonLogFormatter',
                'logger_name': 'srg'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'json'
            },
        },
        'loggers': {
            'srg': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }

    def __init__(self, ctx):
        self._ctx = ctx
        self._logger_prefix = ''
        self._apply_config()

    def set_config(self, cfg):
        self._log_config = cfg

    def set_prefix(self, prefix):
        self._log_config['formatters']['json']['logger_name'] = prefix
        self._log_config['loggers'][prefix] = {'handlers': ['console'], 'level': 'DEBUG'}
        self._apply_config()

    def get_prefix(self):
        return self._logger_prefix

    def _apply_config(self):
        self._logger_prefix = self._log_config['formatters']['json']['logger_name']
        logging.config.dictConfig(self._log_config)

    def get_logger(self, name):
        return logging.getLogger("%s.%s" % (self._logger_prefix, name))
