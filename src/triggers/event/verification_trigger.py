# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.exceptions import DatabaseError
from src.helpers.event import event_handler
from src.globals import get_logger
from src.database.validators import fetch_verified_pks
from src.helpers.validator import check_and_stake


class VerificationTrigger(Trigger):
    """Triggered when there is a new validator approval by the Oracle.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: VERIFICATION)
    """

    name: str = "VERIFICATION"

    def __init__(self) -> None:
        """Initializes a VerificationTrigger object.
        The trigger will process the changes of the daemon after a loop.
        It is a callable object.
        It is used to process the changes of the daemon.
        It can only have 1 action.
        """
        Trigger.__init__(self, name=self.name, action=self.consider_stake)
        get_logger().debug(f"{self.name} is initated.")

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format.
        Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of VerificationIndexUpdated emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    str(event.args.validatorVerificationIndex),
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of VerificationIndexUpdated emits
        """
        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO VerificationIndexUpdated VALUES (?,?,?,?)",
                    events,
                )
            get_logger().debug(f"Inserted {len(events)} events into VerificationIndexUpdated table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table VerificationIndexUpdated") from e

    # pylint: disable-next=unused-argument
    def consider_stake(self, events: Iterable[EventData], *args, **kwargs):
        """If there is a new approval, there is a chance of previously proposed validators being approved.
        Gathers the verified pubkeys and stakes them.
        TODO: (discuss) We don't actually need to parse or save any events as historical data is irrelevant and only the current verificationIndex matters.
        """

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events
        )

        verified_pks: list[str] = fetch_verified_pks()

        check_and_stake(verified_pks)
