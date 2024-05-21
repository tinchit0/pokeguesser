FROM python:3.11.4 AS api
RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD data/ data/
ADD app.py app.py
EXPOSE 80
ENV HOST "0.0.0.0"
ENV PORT "80"
CMD ["python", "app.py"]
