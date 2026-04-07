FROM python

LABEL maintainer="Tushar Verma"
LABEL org.opencontainers.image.authors="tushar.verma@sandisk.com"

ENV container=docker
ENV DEBIAN_FRONTEND=noninteractive
ENV STREAMLIT_SERVER_PORT=80
ENV STREAMLIT_SERVER_COOKIE_SECRET=extrcyviubounoiyvuctyxrcuvyib8s4d651

WORKDIR /app

COPY lib_csv_parser lib_csv_parser
COPY app.py app.py
COPY run.py run.py
COPY requirements.txt requirements.txt

EXPOSE 80

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "./run.py"]