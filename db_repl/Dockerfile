FROM postgres:15

RUN echo "host replication all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf

EXPOSE 5432

CMD ["bash", "-c", "\
PGPASSWORD=$DB_PASSWORD pg_basebackup -h $DB_HOST -D /var/lib/postgresql/data -U $DB_REPL_USER -vP --wal-method=stream && \
echo \"standby_mode = 'on'\" >> /var/lib/postgresql/data/recovery.conf && \
echo \"primary_conninfo = 'host=DB_HOST port=5432 user=$DB_REPL_USER password=$DB_REPL_PASSWORD'\" >> /var/lib/postgresql/data/recovery.conf && \
exec postgres \
"]
