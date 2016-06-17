#!/bin/sh

#/* ****************************************************
# * FileName: lsoftopcgi.sh
# * Author  : ghostwwl
# * Date    : 2013
# * Note    : 跟踪负载最高的那个php-fpm进程
# * ***************************************************/


HPHP_PID=`ps aux|grep "php-fpm"|grep -v 'grep'|awk '{print $3" " $2}'|sort|tail -n 1|awk '{print $2}'`

if [ -n HPHP_PID ]; then
    lsof -p ${HPHP_PID} > "/home/lsof_${HPHP_PID}"
    strace -s 256 -p ${HPHP_PID} > "/home/starce_${HPHP_PID}"
fi
