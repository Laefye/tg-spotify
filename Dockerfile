FROM ubuntu:latest

# Install dependencies for tdlib
RUN apt update && apt install -y \
    make \
    git \
    zlib1g-dev \
    libssl-dev \
    gperf \
    php-cli \
    cmake \
    clang-18 \
    libc++-18-dev \
    libc++abi-18-dev

# Compile and install tdlib
RUN git clone https://github.com/tdlib/td.git && \
    cd td && \
    mkdir build && \
    cd build && \
    CXXFLAGS="-stdlib=libc++" CC=/usr/bin/clang-18 CXX=/usr/bin/clang++-18 cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/usr/local .. && \
    cmake --build . --target install && \
    cd .. && \
    cd .. && \
    ls -l /usr/local && \
    rm -rf td

# Install dependencies for python
RUN apt install -y \
    python3 \
    python3-pip

WORKDIR /app
# Install python dependencies
COPY requirements.txt /app
RUN pip3 install -r requirements.txt

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
ENV TDLIB_LIBRARY_PATH=/usr/local/lib/libtdjson.so

CMD ["python3", "main.py"]
