FROM python:3.10-alpine

WORKDIR /app

RUN python -m venv /myvenv

COPY requirements.txt .
RUN /myvenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/myvenv/bin/python", "-m", "app"]
