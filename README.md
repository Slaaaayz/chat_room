# Comment run le docker :


**Pour lancer le dockerfile :**
```bash
docker build -t chatroom .
docker run -p 7777:6767 chatroom
```

**Pour lancer le docker-compose :**
```bash
docker-compose up --build
```