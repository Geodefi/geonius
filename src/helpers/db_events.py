# -*- coding: utf-8 -*-

from src.globals import SDK, CONFIG


def find_latest_event_block(event_name: str):
    # TODO: check db for given event_name
    return CONFIG.chains[SDK.network.name].first_block
