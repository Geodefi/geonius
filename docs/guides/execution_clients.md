# Execution Clients

## Geth

> [The official documentation](https://geth.ethereum.org/docs) where you can find all the guides and answers you need.

### Installing

There are many ways to install geth!
Please check [this guide](https://geth.ethereum.org/docs/getting-started/installing-geth) for more options and detailed information. This document will explain the required steps while installing and running a geth client on Linux.

#### apt-get

We can easily install geth by:

```bash
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install ethereum
```

#### Build from source

However, AWS does not support `apt-get` so we will utilize `yum` instead and build from source.

Secondly, we will need golang `v1.21^`, and `yum install golang` will supports upto `v1.20`.
We will use some [tricks](https://tecadmin.net/install-go-on-centos/) to install golang v1.21.

```bash
# install golang
sudo dnf update
wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz 
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
source ~/.bashrc
source ~/.bash_profile
go version

# install deps
sudo yum -y update
sudo yum -y install gmp-devel
sudo yum -y install git git-lfs

# clone

git clone https://github.com/ethereum/go-ethereum
# build
cd go-ethereum
make geth
# test
geth version
# ./geth path is : ~/go-ethereum/build/bin/geth
```

> DO NOT run your geth node yet since you did not generate jwt.hex file yet. Geth and Prysm will communicate vie JWT token.

## Nethermind
<!-- TODO -->
## Besu
<!-- TODO -->
## Erigon
<!-- TODO -->