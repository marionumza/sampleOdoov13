FROM odoo:13.0

USER root

RUN apt-get update -y

RUN apt-get install -y python-pandas

RUN pip3 install numpy==1.20.3

RUN pip3 install pandas==1.2.4
