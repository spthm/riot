from copy import deepcopy
from itertools import product
import sys
if sys.version_info < (3, 3):
    from collections import Mapping as ABCMapping
else:
    from collections.abc import Mapping as ABCMapping

from .schemas import _header_schemas, _data_schemas, _default_flags
from .schemas import _MIN_RT_VER, _MAX_RT_VER

class RTSchemaException(Exception):
    def __init__(self, message):
        super(RTSchemaException, self).__init__(message)

class _RTSchemaDict(ABCMapping):
    def __init__(self):
        self._versions = set()
        self._header_schemas = _header_schemas
        self._data_schemas = _data_schemas
        self._default_flags = _default_flags

        self._set_all_versions()
        self._fill_missing_schemas()

    def __contains__(self, key):
        return key in self._versions

    def __getitem__(self, key):
        return (self._header_schemas[key],
                self._default_flags[key],
                self._data_schemas[key])

    def __iter__(self):
        for key in self._versions:
            yield key

    def __len__(self):
        return len(self.keys())

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for key in self.iterkeys():
            yield self[key]

    def iteritems(self):
        for key in self.iterkeys():
            yield key, self[key]

    def _fill_missing_schemas(self):
        schemas = [self._header_schemas, self._data_schemas, self._default_flags]
        for (dct, target_version) in product(schemas, self._versions):
            vers = sorted(dct.keys())
            if target_version not in dct:
                prev_vers = [v for v in vers if v < target_version]
                if prev_vers == []:
                    message = "Schemas incomplete for version " + target_version
                    raise RTSchemaException(message)
                stand_in = prev_vers[-1]
                dct[target_version] = deepcopy(dct[stand_in])

    def _set_all_versions(self):
        self._versions.update(self._header_schemas.keys())
        self._versions.update(self._data_schemas.keys())
        self._versions.update(self._default_flags.keys())
        self._versions.add("%02d%02d" % _MAX_RT_VER)

schema_dict = _RTSchemaDict()
