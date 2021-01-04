import json


class AccountsRecordsEncoder(json.JSONEncoder):
    def default(self, obj):
        obj = dict(obj)
        obj['currency'] = json.loads(obj['currency'])
        obj['params'] = json.loads(obj['params'])
        return obj


class RecordsEncoder(json.JSONEncoder):
    def default(self, obj):
        return dict(obj)
