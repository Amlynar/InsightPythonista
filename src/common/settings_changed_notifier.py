from injector import singleton


@singleton
class SettingsChangedNotifier:
    """Lets Settings tell the Dashboard that new values were saved.

    framework has no screen-to-screen result/callback mechanism.
    """

    def __init__(self):
        self._listeners = []

    def subscribe(self, listener):
        self._listeners.append(listener)

    def notify(self):
        for listener in list(self._listeners):
            listener()
