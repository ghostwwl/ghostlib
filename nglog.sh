#!/bin/sh

#/* ****************************************************
# * FileName: nglog.sh
# * Author  : ghostwwl
# * Date    : 2013.7.10
# * Note    : nginx日志切割
# * ***************************************************/

logpath="/opt/logs"
YESTERDAY=`date -d yesterday +%y%m%d`
# 日志大于多少才开始切分咧
SPLIT_LIMIT=$((1024*1024*100))

#ftp_log_host="192.168.2.***"
#ftp_log_user="backup"
#ftp_log_pwd="******"

for f in $( ls ${logpath}/*.log )
do
	if [ -f "$f" ]; then
		log_file_size=`stat -c%s ${f}`
		if [ $log_file_size -lt $SPLIT_LIMIT ]; then
			#echo "sikp log: ${f} file_size: ${log_file_size}"
			continue
		fi
		dstlog=${f/./_}
		mv ${f} ${dstlog}
		NginxNumber=`ps -ef |grep "nginx"|grep -v "grep"|wc -l`
		if [ $NginxNumber -le 0 ]; then
			echo "Not Found Nginx Runing"
		else
		#	echo "${NginxNumber}"
			kill -USR1 `pgrep -f 'nginx\:\s*master'`
		fi
		dstgzfile=${f/_access.log/}${YESTERDAY}".log.gz"
		/usr/bin/gzip -c ${dstlog} >${dstgzfile}
		#echo "${dstlog} --> ${dstgzfile}"

    # 多个nginx日志的时候 上传到某台linux日志分析机器
		#cd ${logpath}
		#sleep 10
		#echo "----now start upload ${dstgzfile}----"
		#ftp -n <<EOF
		#open $ftp_log_host
		#user $ftp_log_user $ftp_log_pwd
		#binary
		#put $dstgzfile
		#bye
		#EOF
		else
			echo "WARN: ${f} is not file type."
		fi
done

if [ -f /opt/logs/nginx.log ]; then
	echo  "" >/opt/logs/nginx.log
fi
if [ -f /opt/logs/phpcgi.log ]; then
	echo  "" >/opt/logs/phpcgi.log
fi
if [ -f /opt/logs/phpcpu.log ]; then
	echo  "" >/opt/logs/phpcpu.log
fi
if [ -f /usr/local/webserver/php/logs/php-fpm.log ]; then
	echo "" > /usr/local/webserver/php/logs/php-fpm.log
fi
if [ -f /usr/local/webserver/php/logs/slow.log ]; then
	echo "" > /usr/local/webserver/php/logs/slow.log
fi

echo "-- END --"
