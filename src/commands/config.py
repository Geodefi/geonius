# -*- coding: utf-8 -*-

import os
import json
import click

from src.setup import setup
from dotenv import load_dotenv


def reset_config(ctx, option, value):
    if not value or ctx.resilient_parsing:
        return

    click.confirm("Are you sure you want to reset the configuration?", abort=True)
    return value


def config(main_dir: str, main_dir_path: str):

    try:
        _config: dict = {}
        env: dict = {}

        if not os.path.exists(main_dir_path):
            click.confirm(
                f"A folder named '{main_dir}' will be created in the current directory.",
                abort=True,
            )
            os.mkdir(main_dir_path)

        config_path = os.path.join(main_dir_path, "config.json")
        if os.path.exists(config_path):
            click.confirm(
                "Found a config.json file. Confirm the reconfiguration before proceeding.",
                abort=True,
            )

        click.confirm("Chain is selected as 'holesky', please confirm", abort=True)
        _config["chains"] = {
            "holesky": {
                "start": 1550551,
                "identifier": "latest",
                "period": "5",
                "interval": "12",
                "range": "3000",
                "execution_api": "",
                "consensus_api": "",
            }
        }

        _config["operator_id"] = click.prompt("Your operator ID", type=int)
        env["GEONIUS_PRIVATE_KEY"] = click.prompt(
            "What is the private key for the current maintainer of the Node Operator?"
        )

        _config["chains"]["holesky"]["execution_api"] = click.prompt(
            "Please provide the Execution layer endpoint (can utilize <API_KEY_EXECUTION>)",
            type=str,
        )
        if "<API_KEY_EXECUTION>" in _config["chains"]["holesky"]["execution_api"]:
            env["API_KEY_EXECUTION"] = click.prompt(
                "Api key is detected. Please provide the api key"
            )

        _config["chains"]["holesky"]["consensus_api"] = click.prompt(
            "Please provide the Consensus layer endpoint (can utilize <API_KEY_CONSENSUS>)",
            type=str,
        )
        if "<API_KEY_CONSENSUS>" in _config["chains"]["holesky"]["consensus_api"]:
            env["API_KEY_CONSENSUS"] = click.prompt(
                "Api key is detected. Please provide the api key"
            )

        _config["network"] = {"refresh_rate": 60, "max_attempt": 20, "attempt_rate": 0.1}
        _config["strategy"] = {"min_proposal_queue": 0, "max_proposal_delay": 0}
        _config["logger"] = {
            "no_stream": False,
            "no_file": False,
            "dir": "logs",
            "level": "INFO",
            "when": "midnight",
            "interval": 1,
            "backup": 30,
        }

        click.prompt(
            "Set logging level for both terminal and the saved log files",
            type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
            default="INFO",
        )
        _config["ethdo"] = {}
        _config["ethdo"]["wallet"] = click.prompt(
            "What is the name of the ethdo wallet where the validators will be created from?",
            type=str,
            default="geonius",
        )
        env["ETHDO_WALLET_PASSPHRASE"] = click.prompt(
            "What is the passphrase for this wallet?", type=str
        )

        _config["ethdo"]["account_prefix"] = click.prompt(
            f"Validator accounts created on {_config['ethdo']['wallet']} will have a prefix."
            " For example the 31st validator will have a name of geonius/Validator31."
            " What would you like the prefix to be?",
            type=str,
            default="Validator",
        )
        env["ETHDO_ACCOUNT_PASSPHRASE"] = click.prompt(
            "What should the passphrase for these accounts should be?", type=str
        )

        _config["database"] = {"dir": "db"}

        if click.confirm("Would you like to setup the gas oracle service?"):
            _config["gas"] = dict()
            _config["gas"]["api"] = click.prompt(
                "Please provide the api endpoint that responds with the gas prices in gwei"
            )
            if "<API_KEY_GAS>" in _config["gas"]["api"]:
                env["API_KEY_GAS"] = click.prompt("Api key is detected. Please provide the api key")
            _config["gas"]["parser"] = {}
            _config["gas"]["parser"]["base"] = click.prompt(
                "How would you like us to parse base fee?", default="low.suggestedMaxFeePerGas"
            )
            _config["gas"]["max_fee"] = click.prompt(
                "What is the max base fee that geonius can continue to send txs?",
                default=10,
                type=int,
            )
            _config["gas"]["parser"]["priority"] = click.prompt(
                "How would you like us to parse priority fee?",
                default="low.suggestedMaxPriorityFeePerGas",
            )
            _config["gas"]["max_priority"] = click.prompt(
                "What is the max priority fee that geonius can continue to send txs?",
                default=100,
                type=int,
            )

        if click.confirm("Would you like to setup the notification service?"):
            _config["email"] = dict()
            _config["email"]["sender"] = click.prompt("Provide the sender email address")
            _config["email"]["receivers"] = [click.prompt("Provide the receiver email address")]
            _config["email"]["smtp_server"] = click.prompt(
                "Provide the smtp server", default="smtp.gmail.com"
            )
            _config["email"]["smtp_port"] = click.prompt("Provide the smtp port", default="587")
            env["EMAIL_PASSWORD"] = click.prompt(
                "What is the app password provided for geonius by the mail provider?"
            )

        print("Successful configuration.")
        with open(config_path, "w") as outfile:
            json.dump(_config, outfile)
        print("Saved .env...")

        env_path = os.path.join(main_dir_path, ".env")
        with open(env_path, "w") as outfile:
            for key, value in env.items():
                outfile.write(f"{key.upper()}={value}\n")
        print("Saved config.json...")

        print("Confirming the new configuration...")

        load_dotenv(env_path, override=True)

        setup(
            chain="holesky",
            main_dir=main_dir,
            no_log_file=True,
            test_email=True,
            test_ethdo=True,
            test_operator=True,
        )

        print_config(config_path)

    except Exception as e:
        print("Configuration failed, try again.")
        raise e


def print_config(config_path: str):
    try:
        config_dict: dict = json.load(open(config_path, encoding="utf-8"))
        print(json.dumps(config_dict, indent=4))
        print(f"\nconfig.json is located in: {config_path}")
    except Exception:
        print("Could not resolve config.json file. Try with --reset to reconfigure.")


@click.option(
    "--reset",
    required=False,
    is_flag=True,
    callback=reset_config,
    help="Reset the config file and start over. Suggested if there is anything failing.",
)
@click.option(
    "--main-dir",
    envvar="GEONIUS_DIR",
    required=False,
    is_eager=False,
    type=click.STRING,
    default=".geonius",
    help="Relative path for the main directory that will be used to store data. Default is ./.geonius",
)
@click.command(
    help="Prints the current config file and its path."
    " If there is no config file already, helps creating a new one"
    " This command should be called before the first time running geonius."
)
def main(
    main_dir: str,
    reset: bool,
):
    main_dir_path = os.path.join(os.getcwd(), main_dir)

    if reset:
        config(main_dir, main_dir_path)
        return

    config_path = os.path.join(main_dir_path, "config.json")
    if not os.path.exists(config_path):
        config(main_dir, main_dir_path)
        return

    print_config(config_path)
