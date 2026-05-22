from collections import defaultdict


class ExtensionRegistry:
    """Simple event hub reserved for future workflow, notification and audit extensions."""

    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event_name, handler):
        self._handlers[event_name].append(handler)

    def dispatch(self, event_name, payload):
        for handler in self._handlers[event_name]:
            handler(payload)


extension_registry = ExtensionRegistry()
