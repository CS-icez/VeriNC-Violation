FROM tofino:20251025

RUN mkdir /tmp && \
    bash -ic "python3.8 -m pip install --no-cache-dir \
    pyyaml \
    asyncio \
    ipaddress \
    ansicolors \
    readline \
    six"
