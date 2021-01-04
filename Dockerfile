FROM python:3.7-slim

RUN groupadd pygroup && useradd -m -g pygroup -s /bin/bash pyuser
RUN mkdir -p /home/pyuser/app

COPY . /home/pyuser/app
WORKDIR /home/pyuser/app

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /home/pyuser/app/requirements/prod.txt
RUN chown -R pyuser:pygroup /home/pyuser

USER pyuser

CMD ["python", "/home/pyuser/app/pamm/cmd/main.py"]
