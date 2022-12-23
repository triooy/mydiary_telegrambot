FROM python:3.10-slim

RUN apt update 
RUN apt -y install python3-pip
RUN pip3 install --upgrade pip

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/app.py" ]