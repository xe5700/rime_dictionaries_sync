FROM alpine:edge
WORKDIR /app
# 明月拼音/四叶草拼音 词库自动生成工具
# 使用DOCKER环境部署，支持WIN，MAC，LINUX。
ENV USE_BAIDU="False"
ENV USE_SOGOU="True"
ENV CRON_DICT_UPDATE="0 3 */7 * *"
ENV DICT_TYPE="clover"
ENV SOGOU_DIR_RE="单机游戏"
ENV SOGOU_FILE_RE="原神|魔兽|帝国"
ENV BAIDU_DIR_RE="网络游戏"
ENV BAIDU_FILE_RE="百战天虫Online"
ENV RUN_ONCE="False"
ENV USE_RCLONE="False"
ENV REMOTE_CONFIG="remote"
ENV XDG_CONFIG_HOME="/config"
ENV REMOTE_SYNC_PATH="/RIME_DICT/"
ARG imewlconverter_version="2.7.0"
RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
#Use huaweicloud mirror
RUN sed -i "s@http://dl-cdn.alpinelinux.org/@https://mirrors.huaweicloud.com/@g" /etc/apk/repositories

RUN apk add --no-cache python2 tar icu-libs krb5-libs libgcc libintl libssl1.1 libstdc++ zlib python3 opencc py3-pip curl bash tzdata &&\
    python2 -m ensurepip && \
    rm -r /usr/lib/python2*/ensurepip && \
    mkdir -p /app
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --runtime dotnet --install-dir /usr/bin/ && rm -rf /tmp/* && \
chmod +x /usr/bin/dotnet
RUN mkdir -p imewlconverter && \ 
curl -L https://github.com/studyzy/imewlconverter/releases/download/v${imewlconverter_version}/imewlconverter_Linux_Mac.tar.gz | tar xvz -C imewlconverter
VOLUME ["/dicts", "/remote"]
COPY --from=rclone/rclone /usr/local/bin/rclone /usr/local/bin/

ADD app ./
RUN pip2 install user_agent && \
set +e && \
pip3 install -r requirements.txt && \
rm -r /root/.cache
RUN adduser app --system && chmod -R 777 /tmp/ && mkdir /config && chown -R app /app /dicts /remote /config
USER app
CMD ["python3","./app.py" ]
ENV TZ=Asia/Shanghai