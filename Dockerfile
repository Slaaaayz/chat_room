FROM python

WORKDIR /app

ENV CHAT_PORT=6767
ENV MAX_USERS =20

COPY . /app

RUN pip install -r requirements.txt

CMD [ "python", "./serveur.py" ]