from typing import Callable

from src.classes.loggable import Loggable


class Trigger(Loggable):
    """Bound to a Daemon, a Trigger also processes the changes of the daemon after a loop.
    A trigger can only have 1 action.

    Example:
        def action():
            print(datetime.datetime.now())

        t = Trigger(action)
    """

    def __init__(self, name: str, action: Callable):
        """Initializes a helper loggable instance."""

        Loggable.__init__(self, name=name)

        self.__register_action(action)

    def __register_action(self, action: Callable) -> None:
        """Sets an action to be called during processing of the daemon's changes

        Args:
            action: function to be called when Triggered.
        """

        self.__action: Callable = action

    def process(self, *args, **kwargs) -> None:
        """Function that will be triggered to process the registered action."""

        try:
            self.__action(*args, **kwargs)
        except Exception as e:
            raise e
