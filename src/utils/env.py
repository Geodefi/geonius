import os
from dotenv import load_dotenv


def load_env(ctx, option, value):
    if ctx.resilient_parsing:
        return
    load_dotenv(os.path.join(value, ".env"))
    return value
