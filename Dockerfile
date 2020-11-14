FROM alpine:edge
WORKDIR /app
# 明月拼音/四叶草拼音 词库自动生成工具
# 使用DOCKER环境部署，支持WIN，MAC，LINUX。
ENV USE_BAIDU="False"
ENV USE_SOGOU="True"
ENV CRON_DICT_UPDATE="0 3 */7 * *"
ENV DICT_TYPE="clover"
RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
#Use huaweicloud mirror
RUN sed -i "s@http://dl-cdn.alpinelinux.org/@https://mirrors.huaweicloud.com/@g" /etc/apk/repositories

RUN apk add --no-cache python2 tar icu-libs krb5-libs libgcc libintl libssl1.1 libstdc++ zlib python3 opencc py3-pip curl bash &&\
    python2 -m ensurepip && \
    rm -r /usr/lib/python2*/ensurepip
RUN pip2 install user_agent && \
set +e && \
pip install -r requirements.txt && \
rm -r /root/.cache
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --runtime dotnet && rm -rf /tmp/*
ADD app ./
RUN ./bootstrap.sh
VOLUME [ "/dicts" ]
COPY --from=driveone/onedrive:alpine /usr/local/bin/onedrive /usr/local/bin/
#CMD ["python3","./start.py" ]