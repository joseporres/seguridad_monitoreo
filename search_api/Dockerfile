FROM python:3.9

RUN apt-get update && apt-get install -y build-essential cmake

WORKDIR /app

COPY /requirements/base.txt ./

RUN pip install -U pip wheel cmake
RUN pip install --no-cache-dir -r base.txt

COPY . .

EXPOSE 5000

CMD ["python", "."]