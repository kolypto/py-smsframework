from datetime import date, datetime, time
from json import JSONDecoder, JSONEncoder
import inspect


class JsonExEncoder(JSONEncoder):
    """ JsonEx encoder, which can marshall objects and exceptions """
    def default(self, o):
        if isinstance(o, (date, datetime, time)):
            return {'?': [o.__class__.__name__, o.isoformat()]}
        if isinstance(o, BaseException):
            return {'?E': [o.__class__.__name__, o.args]}
        return {'?': [
            o.__class__.__name__,
            o.__dict__
        ]}


class JsonExDecoder(JSONDecoder):
    """ JsonEx decoder, which can un-marshall objects """

    def __init__(self, classes, exceptions, *args, **kwargs):
        """
        :param classes:
                Dict of class names,
                mapped to:
                    - Class
                    - Callable function: lambda **props
                With class, property names MUST match constructor argument names!
                Extra properties are stupidly copied to the object
        :type classes: dict
        :param exceptions:
                Dict of exception class names,
                mapped to:
                    - Class
                    - Callable function: lambda *args
                If exception is not registered -- defaults to RuntimeError
        :type exceptions: dict
        """
        self.classes = classes
        self.exceptions = exceptions

        kwargs['object_hook'] = self.dict_to_object
        super(JsonExDecoder, self).__init__(*args, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        # Special handling for exceptions
        if '?E' in d and len(d) == 1:
            exc, args = d['?E']
            if exc not in self.exceptions:
                # Fallback
                return RuntimeError(*args)
            else:
                E = self.exceptions[exc]
                return E(*args)

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
            if cls in self.classes:
                C = self.classes[cls]
                if inspect.isfunction(C):
                    # Lambda-constructor
                    o = C(**props)
                elif inspect.isclass(C):
                    # Dict constructor
                    if not inspect.ismethod(C.__init__):
                        # Classes without an explicitly declared constructor
                        o = C()
                    else:
                        # Classes with a constructor
                        argspec = inspect.getargspec(C.__init__)

                        # Arguments should be named after properties
                        args = [props.pop(a) for a in argspec.args[1:]]  # (self, (....))

                        # Create object
                        o = C(*args)

                    # And now copy the remaining props
                    for k, v in props.items():
                        setattr(o, k, v)

                    return o

        # Nothing special, return as is
        return d
