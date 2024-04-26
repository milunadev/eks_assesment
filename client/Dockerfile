FROM python:3.12-slim

## Copiando ficheros necesarios y seteando el directorio de trabajo
 
COPY . /home/app
WORKDIR /home/app

EXPOSE 5000

## Instalando dependencias
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

## Lanzando la aplicacion
CMD [ "python3", "main2.py" ]