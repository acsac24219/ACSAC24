FROM rhub/ubuntu-gcc:latest

WORKDIR /home

RUN apt-get update && apt-get install -y \
    graphviz \
    npm  \
    pip  \
    tzdata \
    && ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && pip install cpgqls-client \
    && pip install jproperties \
    && curl -L "https://github.com/joernio/joern/releases/download/v2.0.232/joern-install.sh" -o joern-install.sh \
    && chmod u+x joern-install.sh \
    && sed -i 's/sudo ln -sf/ln -sf/' joern-install.sh \
    && ./joern-install.sh --version=v2.0.232 \
    && rm joern-cli.zip

ENV TZ=America/Chicago


