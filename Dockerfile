## base image
FROM python:3.8.9

## install dependencies
WORKDIR /usr/src/app

## Vamos apenas instalar o que é obrigatório
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt


EXPOSE 5000
CMD ["uvicorn" ,"main:app", "--port", "5000" ]