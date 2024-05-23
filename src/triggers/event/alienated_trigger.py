# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE

from src.logger import log
from src.classes import Trigger, Database
from src.exceptions import DatabaseError
from src.utils import send_email
from src.helpers import (
    create_alienated_table,
    event_handler,
    create_validators_table,
    save_portal_state,
    save_local_state,
    check_pk_in_db,
)


class AlienatedTrigger(Trigger):
    """
    Triggered when a validator proposal is alienated.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: ALIENATED_TRIGGER)
    """

    name: str = "ALIENATED_TRIGGER"

    def __init__(self) -> None:
        """Initializes a AlienatedTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.alienate_validators)
        create_validators_table()
        create_alienated_table()
        log.debug(f"{self.name} is initated.")

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is in the validators table.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is in the validators table, False otherwise
        """

        # if pk is in db (validators table), then continue
        return check_pk_in_db(event.args.pubkey)

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of Alienated emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    event.args.pubkey,  # TEXT
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of saveable events
        """

        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO Alienated VALUES (?,?,?,?)",
                    events,
                )
            log.debug(f"Inserted {len(events)} events into Alienated table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table Alienated") from e

    def alienate_validators(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Alienates the validators in the database. Updates the database local and portal state of the validators to ALIENATED.

        Args:
            events (Iterable[EventData]): list of events
        """
        log.info(f"{self.name} is triggered.")

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        if filtered_events:
            log.critical("You are possibly prisoned!")

            for event in filtered_events:
                pubkey: str = event.args.pubkey
                log.critical(f"Your validator is alienated: {pubkey}")
                save_portal_state(pubkey, VALIDATOR_STATE.ALIENATED)
                save_local_state(pubkey, VALIDATOR_STATE.ALIENATED)

            send_email(
                "AlienatedAndPrisoned",
                "Alienated event is triggered, you will be prisoned. Please contact the admin and exit the program.",
                [("<file_path>", "<file_name>.log")],
            )
