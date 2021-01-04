from json import dumps
from time import time
from logging import StreamHandler
from pamm.constants import LogTypes


class ConsoleStreamHandler(StreamHandler):
    @staticmethod
    def format_message(record):
        msg = {
            'datetime': int(time()),
            'source': record.name,
            'level': record.levelname,
        }
        if type(record.msg) == str:
            msg['type'] = LogTypes.TYPE_MESSAGE
            msg['message'] = record.msg
        else:
            msg['context'] = record.msg
            if type(record.args) == dict:
                msg['name'] = record.args.get('event_name', None)
                msg['chain'] = record.args.get('chain', None)

        return dumps(msg, sort_keys=True, separators=(',', ':', ))

    def emit(self, record):
        try:
            record.msg = self.format_message(record)
        finally:
            pass
        super(ConsoleStreamHandler, self).emit(record)
