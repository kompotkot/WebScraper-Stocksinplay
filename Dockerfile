from alpine:latest

ENV RUNTIME_PACKAGES python3 py3-pip libxslt libxml2
ENV BUILD_PACKAGES python3-dev libxslt-dev libxml2-dev libffi-dev openssl-dev gcc linux-headers musl-dev

RUN apk --update add --no-cache ${RUNTIME_PACKAGES} ${BUILD_PACKAGES} \
  && pip3 install --upgrade pip \
  && pip3 install scrapy gspread oauth2client \
  && apk del ${BUILD_PACKAGES} \
  && rm -rf /root/.cache

WORKDIR /var/app

COPY . /var/app

ENTRYPOINT ["python3"]

CMD ["app.py","-h"]