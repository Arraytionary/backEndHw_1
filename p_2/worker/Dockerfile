# Build upon this image "alpine" is a lightweight distro
FROM python:3.7-alpine

# Copy requirements.txt
#COPY ./requirements.txt /app/requirements.txt

# Install all the requirements
#RUN pip install -r /app/requirements.txt

# Copy everthing from . to /app inside the 'box'
COPY . /app
WORKDIR /app



RUN mkdir -p /app/out
RUN apk --no-cache add msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f
RUN apk --update add --no-cache file imagemagick build-base jpeg-dev zlib-dev
ENV MAGICK_HOME=/usr
RUN apk add --no-cache imagemagick-dev

ENV LIBRARY_PATH=/lib:/usr/lib
VOLUME /app/out
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN python -c 'import imageio; imageio.plugins.ffmpeg.download();'
ADD make_thumbnail make_thumbnail
RUN ln -s /app/make_thumbnail /bin/make_thumbnail
RUN chmod +x /app/make_thumbnail

# How to run it when we start up the box?
CMD ["./worker.py"]