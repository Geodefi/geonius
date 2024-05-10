# Consensus Clients

# Nimbus

> [The helper documentation](https://nimbus.guide) where you can find all the guides and answers you need.
>
### Installing

We can easily install nimbus by:

#### apt-get

```bash
mkdir -p nimbus-eth2
tar xvf nimbus-eth2_Linux_amd64_22.6.1_2444e994.tar.gz --strip-components 1 -C nimbus-eth2
```

#### Build from source

However, AWS does not support `apt-get` so we will build from source instead.

```bash
# clone
git clone https://github.com/status-im/nimbus-eth2
cd nimbus-eth2

# build (can take several minutes)
make -j4 nimbus_beacon_node
# test
build/nimbus_beacon_node --help
# 
```

# Lighthouse
<!-- TODO -->
# Prysm
<!-- TODO -->
# Teku
<!-- TODO -->