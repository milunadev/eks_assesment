FROM python:3.10-slim

## Copiando ficheros necesarios y seteando el directorio de trabajo
## COPY ./server /home/app #si usamos compose para testing
COPY . /home/app   
WORKDIR /home/app


## Instalando dependencias
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

## Lanzando la aplicacion
CMD [ "python3", "-u", "main.py" ]