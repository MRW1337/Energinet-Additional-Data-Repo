FROM python:3.11

WORKDIR /App
COPY . .

EXPOSE 80

CMD ["python", "main.py"]

