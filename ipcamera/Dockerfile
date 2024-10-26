FROM aler9/rtsp-simple-server
FROM ubuntu:latest
RUN apt update -y && apt install -y ffmpeg
COPY cmd.sh cmd.sh
COPY rtsp.yml /rtsp-simple-server.yml
COPY --from=0 /mediamtx /mediamtx
ENTRYPOINT ["bash", "/cmd.sh"]