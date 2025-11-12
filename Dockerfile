
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python build_website.py

FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN rm index.html

COPY --from=builder /app/*.html .
COPY --from=builder /app/charts_static ./charts_static
COPY --from=builder /app/charts_interactive ./charts_interactive

EXPOSE 80