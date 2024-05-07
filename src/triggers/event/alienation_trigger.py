# -*- coding: utf-8 -*-

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
    """

    name: str = "ALIENATION_TRIGGER"

    def __init__(self) -> None:
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.alienate_validators)
        create_validators_table()
        create_alienation_table()

    def __filter_events(self, event: dict) -> bool:
        """Filters the events based on the validators table.

        Args:
            event(dict) : event to be filtered

        Returns:
            bool : True if the event is in the validators table, False otherwise
        """

        # if pk is in db (validators table), then continue
        with Database() as db:
            db.execute(
                f"""
                    SELECT pubkey FROM {validators_table}
                    WHERE pubkey = {event.args.pubkey}
                """
            )
            res = db.fetchone()  # returns None if not found
        if res:
            return True
        else:
            return False

    def __parse_events(self, events: list[dict]) -> list[tuple]:
        """Parses the events and returns a list of tuples.

        Args:
            events(list[dict]) : list of Alienated emits

        Returns:
            List[tuple] : list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            pubkey: int = event.args.pubkey
            block_number: int = event.blockNumber
            block_hash: str = event.blockHash
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            transaction_hash: str = event.transactionHash
            address: str = event.address

            saveable_events.append(
                (
                    pubkey,
                    block_number,
                    block_hash,
                    log_index,
                    transaction_index,
                    transaction_hash,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]):
        """Saves the events to the database.

        Args:
            events(list[tuple]) : list of saveable events
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO alienation VALUES (?,?,?,?,?,?,?)",
                events,
            )

    def alienate_validators(self, events: list[dict], *args, **kwargs):
        """
        Updates the local_state and portal_state for validator pubkeys Alienated.

        Args:
            events(int) : sorted list of "Alienated" emits
        """

        # filter, parse and save events
        filtered_events: list[dict] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        alien_pks: list[int] = [x.args.pubkey for x in filtered_events]

        for pk in alien_pks:
            save_portal_state(pk, VALIDATOR_STATE.ALIENATED)
            save_local_state(pk, VALIDATOR_STATE.ALIENATED)
