from time import sleep
from typing import Callable
from threading import Thread, Event
from src.classes.trigger import Trigger
from src.classes.loggable import Loggable
from src.utils.error import DaemonError


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

    Attributes:
        __interval (int): Time duration between 2 tasks.
        __initial_delay (int): Initial delay before starting the loop.
        __task (Callable): Work to be done after every iteration.
        __worker (Thread): Thread object to run the loop.
        triggers (list[Trigger]): list of initialized Trigger instances.
        start_flag (Event): Event flag to start the daemon.
        stop_flag (Event): Event flag to stop the daemon.
    """

    def __init__(
        self,
        name: str,
        interval: int,
        task: Callable,
        triggers: list[Trigger],
        initial_delay: int = 0,
    ) -> None:
        """Initializes a Daemon object. The daemon will run the task with the given interval.

        Args:
            name (str): name of the daemon to be used when logging etc.
            interval (int): Time duration between 2 tasks.
            task (Callable): Work to be done after every iteration
            triggers (list[Trigger]): list of initialized Trigger instances
            initial_delay (int, optional): Initial delay before starting the loop. Defaults to 0.
        """

        Loggable.__init__(self, name=name)

        self.__set_task(task)
        self.__set_interval(interval)
        self.__set_initial_delay(initial_delay)
        self.__set_triggers(triggers)

        # TODO: should consider using daemon threads
        self.__worker: Thread = Thread(name="background", target=self.__loop)
        self.start_flag: Event = Event()
        self.stop_flag: Event = Event()

    @property
    def interval(self) -> int:
        """Returns waiting period (in seconds), as a property

        Returns:
            int: Waiting period in seconds
        """

        return self.__interval

    @property
    def initial_delay(self) -> int:
        """Returns initial delay before starting the loop, as a property

        Returns:
            int: Initial delay in seconds
        """

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
            triggers (list[Trigger]): list of initialized Trigger instances
        """

        self.triggers: list[Trigger] = triggers

    def __loop(self) -> None:
        """Runs the loop, checks for the task and triggers on every iteration. Stops when stop_flag is set.

        If the task raises an exception, the daemon stops and raises a DaemonStoppedException. This is to prevent
        the daemon from running with a broken task. The exception is raised to the caller to handle the error. The
        daemon can be restarted after the error is handled. The stop_flag is set to prevent the daemon from running again.

        Raises:
            DaemonError: Raised if the daemon stops due to an exception.
        """

        sleep(self.__initial_delay)

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
                raise DaemonError("Daemon stopped due to an exception.") from e

    def run(self) -> None:
        """Starts the daemon, runs the loop when called.

        Raises:
            DaemonError: Raised if the daemon is already running.
        """

        # if already started
        if self.start_flag.is_set():
            raise DaemonError("Daemon is already running.")
        self.stop_flag.clear()

        self.__worker.start()

        self.logger.info(f"running. Use stop() to stop, and CTRL+Z to exit.")
        self.start_flag.set()

    def stop(self) -> None:
        """Stops the daemon, exits the loop.

        Raises:
            DaemonError: Raised if the daemon is already stopped.
        """

        # if already stopped
        if not self.start_flag.is_set() or self.stop_flag.is_set():
            raise DaemonError("Daemon is already stopped.")

        self.stop_flag.set()
