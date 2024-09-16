FROM python:3.10
WORKDIR /app
RUN python -m venv venv
RUN . venv/bin/activate
RUN pip install --upgrade pip
RUN pip install setuptools wheel
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]