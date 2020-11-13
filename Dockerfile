FROM alpine
WORKDIR /app
ENV DICTS="(计算机|日本|官方推荐|大全).*\.scel$"
RUN apk add --no-cache python2 fd parallel git
ADD rime-sogou-dictionaries .
RUN ./bootstrap.sh
RUN ["make-dict.sh" ,DICTS]