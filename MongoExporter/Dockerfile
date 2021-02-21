FROM alpine

COPY mongoexporter.ini /conf
COPY MongoExporter /bin
COPY start.sh /bin

EXPOSE 30000-40000

RUN chmod 777 /bin/start.sh && chmod 777 /bin/MongoExporter
ENTRYPOINT ["sh", "/bin/start.sh"]
#ENTRYPOINT ["ls", "/bin"]
