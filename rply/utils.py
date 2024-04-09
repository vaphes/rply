from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any


class IdentityDict(MutableMapping):
    def __init__(self):
        self._contents: dict[int, Any] = {}
        self._keepalive: list[Any] = []

    def __getitem__(self, key: Any):
        return self._contents[id(key)][1]

    def __setitem__(self, key: Any, value: Any):
        idx = len(self._keepalive)
        self._keepalive.append(key)
        self._contents[id(key)] = key, value, idx

    def __delitem__(self, key: Any):
        del self._contents[id(key)]
        for idx, obj in enumerate(self._keepalive):
            if obj is key:
                del self._keepalive[idx]
                break

    def __len__(self):
        return len(self._contents)

    def __iter__(self):
        for key, _, _ in itervalues(self._contents):
            yield key


@dataclass
class Counter:
    value: int = 0

    def incr(self):
        self.value += 1


def itervalues(d: dict):
    return d.values()


def iteritems(d: dict):
    return d.items()
