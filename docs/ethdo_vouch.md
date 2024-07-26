# Ethdo & Vouch

## Ethdo

### Installation

[Ethdo](https://github.com/wealdtech/ethdo) is a golang package can be easily installed with:

```bash
go install github.com/wealdtech/ethdo@latest
```

It is important that `ethdo` is registered as a path. To check it:

```bash
ethdo version
```

### Creating a wallet & account

Now that we are done with the installation we should create a wallet for geonius.

```bash
ethdo wallet create --wallet="__wallet name__"  --wallet-passphrase="__wallet passphrase__" --type="hd"
```

Then, we can create an account on this wallet:

```bash
ethdo account create --account="__wallet name__/__account name__" --wallet-passphrase="__wallet passphrase__" --passphrase="__account passphrase__"
```

## Vouch

> Prysm must be started with the `--enable-debug-rpc-endpoints` option for Vouch to operate correctly.
>
### Installation

```bash
go get github.com/attestantio/vouch
```

#### Configuration

Create a **.vouch.yml** according to your setup. Here is a [detailed guide](https://github.com/attestantio/vouch/blob/master/docs/configuration.md).

> Vouch's configuration file can be written in `JSON` or `YAML`. The file can either be in the user's home directory, in which case it will be called `.vouch.json` (or `.vouch.yml)`, or it can be in a directory specified by the command line option `--base-dir` or environment variable `VOUCH_BASE_DIR`, in which case it will be called `vouch.json` (or `vouch.yml).

Example:

```yml
log-file: /home/vouch.log
log-level: "info"

graffiti:
  static:
    value: "IceBear strikes again"

beacon-node-addresses: ["localhost:5052"]

accountmanager:
  wallet:
    accounts:
      - __wallet name__
    passphrases:
      - __account passphrase__
```

#### Starting Vouch

To start Vouch type:

```bash
vouch
```
<!-- 
> Please note that the wallet keymanager does not provide slashing protection. It is recommended that the Dirk keymanager be used for all production installations, due to the additional protections it provides.

## Dirk

Attestant provides two separate products, Vouch for the validator client and Dirk for signer, resulting in lower complexity in each of the products, a cleaner architecture, and the ability to separate security domains.

Optionally, [Dirk](https://github.com/attestantio/dirk) can be configured with ethdo & Vouch as a wallet manager.

Although it is not covered within the documentation provided here, it is **highly recommended** to utilize its functionality to create a safer environment for your validator servers with distributed signing.

Here is the d -->
