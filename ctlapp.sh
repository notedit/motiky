#! /usr/bin/env  bash

# Author: liulianxiang <notedit@gmail.com>


MAINMODULE=manage:app

case $1 in
    start)
        exec gunicorn -D -w 4 -k gevent -p /tmp/motiky.pid -b 127.0.0.1:9090 $MAINMODULE
        ;;
    stop)
        kill -INT `cat /tmp/motiky.pid`
        ;;
    restart)
        kill -INT `cat /tmp/motiky.pid`
        exec gunicorn -D -w 4 -k gevent -p /tmp/motiky.pid -b 127.0.0.1:9090 $MAINMODULE
        ;;
    debug)
        exec gunicorn  -w 4  -p /tmp/motiky.pid -b 127.0.0.1:9090 $MAINMODULE
        ;;
    *)
        echo "./ctlapp.sh start | stop | debug | debug"
        ;;
esac
