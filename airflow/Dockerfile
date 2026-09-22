FROM apache/airflow:3.0.0
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN echo "/opt/airflow/api-request" > /home/airflow/.local/lib/python3.12/site-packages/api-request.pth
