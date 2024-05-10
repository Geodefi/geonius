# A Novel Approach on Client Diversity

Here is a helper article that explains the setup we are going for.
<https://medium.com/coinmonks/creating-ethereum-2-withdrawal-keys-using-ethdo-6e41b14ddd7b>

## ethdo

#### Installing

[Ethdo](https://github.com/wealdtech/ethdo) is a golang package can be easily installed with:

```bash
go install github.com/wealdtech/ethdo@latest
ethdo version
```

#### Configuration

Create a wallet:
> `wallet-passphrase` is optional

```bash
ethdo wallet create --wallet="geonius" --type="hd" --wallet-passphrase="my wallet secret"
```

Create an account bound to the wallet:

```bash
ethdo account create --account="geonius/validators" --wallet-passphrase="my wallet secret" --passphrase="my account secret"
```

This is enough for now.

## Vouch

Vouch is designed to work with multiple beacon nodes using strategies. A strategy allows Vouch intelligently to decide which actions to take in which situations, in order to provide the optimum validating service.

[Vouch](https://github.com/attestantio/vouch)

#### Installing

```bash
go install github.com/attestantio/vouch@latest
vouch version
```

#### Configuration

Create a **.vouch.yml** according to your setup. Here is a [detailed guide](https://github.com/attestantio/vouch/blob/master/docs/configuration.md).

> Vouch's configuration file can be written in `JSON` or `YAML`. The file can either be in the user's home directory, in which case it will be called `.vouch.json` (or `.vouch.yml)`, or it can be in a directory specified by the command line option `--base-dir` or environment variable `VOUCH_BASE_DIR`, in which case it will be called `vouch.json` (or `vouch.yml).

Example:

```yml
log-file: /home/ec2-user/vouch.log
log-level: 'debug'
graffiti:
  static:
    value: 'IceBear strikes again'
beacon-node-addresses: ['localhost:5052']
accountmanager:
  wallet:
    accounts:
    - geonius/validators
    passphrases:
    - Aid7nisaej9shoodohyaec4o
blockrelay:
  fallback-fee-recipient: '0x0000000000000000000000000000000000000000'
```

## Dirk

Attestant provides two separate products, Vouch for the validator client and Dirk for signer, resulting in lower complexity in each of the products, a cleaner architecture, and the ability to separate security domains.

Optionally, [Dirk](https://github.com/attestantio/dirk) can be configured with ethdo & Vouch as a wallet manager.

Although it is not covered within the documentation provided here, it is highly recommended to utilize its functionality to create a safer environment for your validator servers with distributed signing.
