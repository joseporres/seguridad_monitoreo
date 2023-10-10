FROM python:3.9

RUN apt-get update && apt-get install -y build-essential cmake

WORKDIR /app

COPY /requirements/base.txt ./

RUN pip install -U pip wheel cmake
RUN pip install --no-cache-dir -r base.txt

COPY . .

# SET MONGO URI IN .ENV TO mongodb://root:root@mongodb:27017
RUN sed -i 's/mongodb:\/\/root:root@localhost:27017/mongodb:\/\/root:root@mongodb:27017/' .env

# RUN python -m app.seeder.seeder

EXPOSE 5000

CMD ["python", "."]