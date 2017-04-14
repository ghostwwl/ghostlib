#!/bin/sh

# 删除过期的同步日志
times=`date -d '20 minutes ago' +%s`000000000;
/usr/local/ktserver/bin/ktremotemgr slave -ur -ts $times -host localhost -port 11201
/usr/local/ktserver/bin/ktremotemgr slave -ur -ts $times -host localhost -port 11202
