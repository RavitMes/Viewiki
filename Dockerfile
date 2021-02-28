FROM python:3.8-buster
RUN mkdir /wiki_scraper
ADD . .
RUN pip install -r requirments.txt
RUN apt-get update \
&& apt-get install -y graphviz
CMD python main.py

