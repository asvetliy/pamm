import json
import importlib

from pamm.core.helpers import get_from_path


class EventObject:
    def __init__(self, name, attributes, options):
        self.options = options
        self.name = name
        self.attributes = attributes

    @classmethod
    def make_from_event(cls, event_message: dict, event_name: str, event_config: dict):
        options = event_config
        name = event_name
        attributes = {}
        for key, value in options['attributes'].items():
            attributes[key] = get_from_path(event_message, value)
        return cls(name, attributes, options['options'])

    def to_dict(self):
        return {
            'attributes': self.attributes,
            'name': self.name,
            'options': self.options
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def make_request_object(self):
        if 'request_object_type' not in self.options:
            return None
        class_name = self.options['request_object_type'] + 'RequestObject'
        module = importlib.import_module('pamm.core.use_cases.request_objects')
        request_object_class = getattr(module, class_name, None)
        if request_object_class is None:
            return None
        return request_object_class.validate(self.attributes)
