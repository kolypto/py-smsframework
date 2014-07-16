from datetime import date, datetime, time
from json import JSONDecoder, JSONEncoder

from smsframework.data import *

class JsonExEncoder(JSONEncoder):
    """ JsonEx encoder, which can marshall objects """
    def default(self, o):
        if isinstance(o, (date, datetime, time)):
            return {'?': [o.__class__.__name__, o.isoformat()]}
        return {'?': [
            o.__class__.__name__,
            o.__dict__
        ]}

class JsonExDecoder(JSONDecoder):
    """ JsonEx decoder, which can un-marshall objects """

    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.dict_to_object
        super(JsonExDecoder, self).__init__(*args, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        # Special handling for objects
        if '?' in d and len(d) == 1:
            cls, props = d['?']

            # Special handling for dates
            if cls == 'datetime':
                return datetime.strptime(props, '%Y-%m-%dT%H:%M:%S.%f')
            elif cls == 'date':
                return datetime.strptime(props, '%Y-%m-%d').date()
            elif cls == 'time':
                return datetime.strptime(props, '%H:%M:%S.%f').time()

            # Other classes
            print cls, props  # TODO: unserialize objects! How to cope with the constructor? require empty arguments? add helper methods?

        # As is
        return d



from json import dumps, loads
msg = OutgoingMessage('97097418', 'Hi man')

s = dumps({
              'a': msg,
              'n': datetime.utcnow(),
              'd': datetime.utcnow().date(),
              't': datetime.utcnow().time(),
              }, cls=JsonExEncoder)
o = loads(s, cls=JsonExDecoder)
print '--------------\n', o
