FROM django:1.9.4-python2
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 8000
CMD uwsgi --socket 0.0.0.0:8000 --chdir /code --wsgi-file DataComm/wsgi.py --master