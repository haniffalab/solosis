FROM ubuntu:22.04

ARG samtools_version=1.18
RUN apt-get update && apt-get -y upgrade && \
	apt-get install -y build-essential wget procps libncurses5-dev zlib1g-dev \
		libbz2-dev liblzma-dev libcurl3-dev biobambam2 && \
	apt-get clean && apt-get purge && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /tmp
RUN wget https://github.com/samtools/samtools/releases/download/${samtools_version}/samtools-${samtools_version}.tar.bz2 && \
	tar jxf samtools-${samtools_version}.tar.bz2 && \
	rm samtools-${samtools_version}.tar.bz2 && \
	cd samtools-${samtools_version} && \
    ./configure --prefix=/usr/local/  && \
    make && \
    make install && \
    rm -rf samtools-${samtools_version}
