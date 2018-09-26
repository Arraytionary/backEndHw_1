FROM ubuntu:16.04
RUN apt-get update && apt-get install -y \
	imagemagick \
	python3-pip
RUN pip3 install --upgrade pip
# ARG PATH=/bin
WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
COPY make_thumbnail /bin
# RUN ln -s /app/vid_con.py $PATH/make_thumbnail
# RUN ls -la $PATH

