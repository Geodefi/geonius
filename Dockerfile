FROM  ubuntu:24.04

# Install dependencies
# install python
RUN apt-get update

RUN apt-get install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl git \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

RUN apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

# RUN apt-get update && apt-get install -y python3.6 python3-distutils python3-pip python3-apt

# RUN apt-get install -y python3.9 python3-pip

# install golang
RUN apt-get install -y golang-go

# set up go environment
ENV GOROOT=/usr/lib/go
ENV GOPATH=$HOME/go
ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH

# install ethdo with go
RUN go install github.com/wealdtech/ethdo@latest
RUN export PATH=$PATH:$(go env GOPATH)/bin

# install vouch with go
RUN go install github.com/attestantio/vouch@latest

# install pyenv
RUN curl https://pyenv.run | bash
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
RUN echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN exec $SHELL
RUN pyenv update

# install python3.9
RUN pyenv install 3.9


# install pipx
RUN apt-get update
RUN apt-get install -y pipx
RUN pipx ensurepath
RUN exec $SHELL


# install poetry
RUN pipx install poetry
RUN poetry config virtualenvs.prefer-active-python true


# clone geonius
RUN git clone https://crashbandicoott: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@github.com/Geodefi/geonius
RUN cd geonius


RUN poetry env use /root/.pyenv/versions/3.9.19/bin/python
RUN source /root/.cache/pypoetry/virtualenvs/geonius-ASgelVWk-py3.9/bin/activate
RUN poetry install

