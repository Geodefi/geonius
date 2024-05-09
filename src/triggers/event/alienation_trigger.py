# -*- coding: utf-8 -*-

from typing import Any, List, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from src.classes import Trigger, Database
from src.globals import CONFIG
from src.helpers.db_events import create_alienation_table, event_handler
from src.helpers.db_validators import (
    create_validators_table,
    save_portal_state,
    save_local_state,
)

validators_table: str = CONFIG.database.tables.pools.name


class AlienationTrigger(Trigger):
    """
    Triggered when a validator proposal is alienated.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: ALIENATION_TRIGGER)
    """

    name: str = "ALIENATION_TRIGGER"

    def __init__(self) -> None:
        """Initializes a AlienationTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.alienate_validators)
        create_validators_table()
        create_alienation_table()

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is in the validators table.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is in the validators table, False otherwise
        """

        # if pk is in db (validators table), then continue
        with Database() as db:
            db.execute(
                f"""
                    SELECT pubkey FROM {validators_table}
                    WHERE pubkey = {event.args.pubkey}
                """
            )
            res: Any = db.fetchone()  # returns None if not found
        if res:
            return True
        else:
            return False

    def __parse_events(self, events: Iterable[EventData]) -> List[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): List of Alienation emits

        Returns:
            List[tuple]: List of saveable events
        """

        saveable_events: List[tuple] = []
        for event in events:
            pubkey: int = event.args.pubkey
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex
            address: str = event.address

            saveable_events.append(
                (
                    pubkey,
                    block_number,
                    transaction_index,
                    log_index,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: List[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (List[tuple]): List of saveable events
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO alienation VALUES (?,?,?,?,?,?,?)",
                events,
            )

    def alienate_validators(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Alienates the validators in the database. Updates the database local and portal state of the validators to ALIENATED.

        Args:
            events (Iterable[EventData]): List of events
        """

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        alien_pks: List[int] = [x.args.pubkey for x in filtered_events]

        for pk in alien_pks:
            save_portal_state(pk, VALIDATOR_STATE.ALIENATED)
            save_local_state(pk, VALIDATOR_STATE.ALIENATED)
