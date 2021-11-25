FROM ghcr.io/ludeeus/devcontainer/integration:stable

RUN apt update \
    && sudo apt install -y libpcap-dev ffmpeg vim curl jq libturbojpeg0 \
    && mkdir -p /opt \
    && cd /opt \
    && git clone --depth=1 -b dev https://github.com/home-assistant/core.git hass \
    && python3 -m pip --disable-pip-version-check install --upgrade ./hass \
    && ln -s /workspaces/unifiprotect/custom_components/unifiprotect /opt/hass/homeassistant/components/unifiprotect
