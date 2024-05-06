# -*- coding: utf-8 -*-

from geodefi.globals import VALIDATOR_STATE
from src.classes import Trigger
from src.helpers.db_events import create_alienation_table
from src.helpers.db_validators import (
    create_validators_table,
    save_portal_state,
    save_local_state,
)


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

    def alienate_validators(self, events: list[dict], *args, **kwargs):
        """
        Updates the local_state and portal_state for validator pubkeys Alienated.

        Args:
            events(int) : sorted list of "Alienated" emits
        """
        # TODO: for all event triggers: filter + parse + save_db => handler
        # events = event_handler(filter_events(),parse_events(),save_events()) => do this to all event triggers

        alien_pks: list[int] = [x.args.pubkey for x in events]
        # TODO: filter if pk is in db and then continue

        for pk in alien_pks:
            save_portal_state(pk, VALIDATOR_STATE.ALIENATED)
            save_local_state(pk, VALIDATOR_STATE.ALIENATED)
