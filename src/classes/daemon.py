from time import sleep
from typing import Callable
from threading import Thread, Event
from src.classes.trigger import Trigger
from src.classes.loggable import Loggable
from src.globals.exceptions import DeadDaemonException, DaemonStoppedException


class Daemon(Loggable):
    """A daemon repeats a specific task with given interval as a period.
    Daemons use a single thread to run a loop at the background to run all the provided triggers,
    and check for tasks on every iteration.

    .. code-block:: python
        def print_time():
            print(datetime.datetime.now())

        def quick_run():
            a = Daemon(interval=3, task=print_time)
            a.run()

        quick_run()

        a.stop()
    """

    def __init__(
        self,
        name: str,
        interval: int,
        task: Callable,
        triggers: list[Trigger],
        initial_delay: int = 0,
    ):
        """Initializes a Daemon object.

        Args:
            name (str): name of the daemon to be used when logging etc.
            interval (int): Time duration between 2 tasks.
            task (Callable): Work to be done after every iteration
            triggers (list[Trigger]): List of initialized Trigger instances
            initial_delay (int, optional): Initial delay before starting the loop. Defaults to 0.
        """

        Loggable.__init__(self, name=name)

        self.__set_task(task)
        self.__set_interval(interval)
        self.__set_initial_delay(initial_delay)
        self.__set_triggers(triggers)

        # TODO: should consider using daemon threads
        self.__worker = Thread(
            name="background", target=self.__loop, args=(initial_delay,)
        )
        self.start_flag: Event = Event()
        self.stop_flag: Event = Event()

    @property
    def interval(self) -> int:
        """Returns waiting period (in seconds), as a property"""

        return self.__interval

    @property
    def initial_delay(self) -> int:
        """Returns initial delay before starting the loop, as a property"""

        return self.__initial_delay

    def __set_interval(self, interval: int) -> None:
        """Sets waiting period to given interval on initialization.

        Args:
            interval (int): New waiting period
        """

        self.__interval: int = interval

    def __set_initial_delay(self, initial_delay: int) -> None:
        """Sets initial delay before starting the loop, on initialization.

        Args:
            initial_delay (int): New initial delay
        """

        self.__initial_delay: int = initial_delay

    def __set_task(self, task: Callable) -> None:
        """Sets the task for the deamon on initialization.
        Tasks should return a dict of effects to be checked by triggers.

        Args:
            task (function): New task to be done after every period.
        """

        self.__task: Callable = task

    def __set_triggers(self, triggers: list[Trigger]) -> None:
        """Sets list of triggers that will be checked on every iteration, called on initialization.

        Args:
            triggers (list): list of Trigger object entities.
        """

        self.triggers: list[Trigger] = triggers

    def __loop(self, initial_delay: int) -> None:
        """The main function of the Daemon, the loop.
        Waits for self.interval and checks for the triggers after running the tasks.

        Args:
            initial_delay (int): Initial delay before starting the loop.
        """

        sleep(initial_delay)

        while not self.stop_flag.wait(self.interval):
            try:
                result: bool = self.__task()

                if result:
                    # check for the triggers and run the actions
                    if self.triggers:
                        # pylint: disable-next=expression-not-assigned
                        [f.process(result) for f in self.triggers]

            except Exception as e:
                self.start_flag.clear()
                self.stop_flag.set()
                raise DaemonStoppedException from e

    def run(self) -> None:
        """Starts the daemon, runs the loop when called."""

        # if already started
        if self.start_flag.is_set():
            raise DeadDaemonException
        self.stop_flag.clear()

        self.__worker.start()

        self.logger.info(f"running. Use stop() to stop, and CTRL+Z to exit.")
        self.start_flag.set()

    def stop(self) -> None:
        """Stops the daemon, exits the loop."""

        # if already stopped
        if not self.start_flag.is_set() or self.stop_flag.is_set():
            raise DeadDaemonException

        self.stop_flag.set()
