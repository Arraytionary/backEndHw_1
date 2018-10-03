FROM python:3.7-alpine
RUN mkdir -p /app/out
RUN apk --update add --no-cache file imagemagick build-base jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
VOLUME /app/out
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN python -c 'import imageio; imageio.plugins.ffmpeg.download();'
ADD make_thumbnail.py make_thumbnail.py
RUN ln -s /app/make_thumbnail.py /bin/make_thumbnail
RUN chmod +x /app/make_thumbnail.py