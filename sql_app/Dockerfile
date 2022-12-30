FROM python:3.10
WORKDIR /code/
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN mkdir "sql_app"
COPY ./ ./sql_app
EXPOSE 80
CMD ["uvicorn", "sql_app.Controller.main:app", "--host", "0.0.0.0", "--port", "80"]



