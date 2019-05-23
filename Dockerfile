FROM python:latest
ADD . .
COPY ./requirements.txt .
RUN pip install -r requirements.txt
WORKDIR .
CMD ["python", "tabletop.py"]
