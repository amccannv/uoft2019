FROM python:3.6
RUN apt-get update && apt-get install -y \ 
libasound-dev \
portaudio19-dev \
libportaudio2 \
libportaudiocpp0

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN ./setup
COPY . .
CMD [ "python", "app.py" ]
