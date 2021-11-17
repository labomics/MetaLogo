/etc/init.d/redis_6379 start
supervisord -c /etc/supervisord.conf
GUNICORN_CMD_ARGS='--workers 10 --timeout 300 --threads 10 -b 0.0.0.0:8050 --access-logfile MetaLogo/logs/access.log --error-logfile MetaLogo/logs/err.log --capture-output --access-logformat "%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"" ' gunicorn MetaLogo.server.index:server