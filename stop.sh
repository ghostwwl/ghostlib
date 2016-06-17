#!/bin/sh

#/* ****************************************************
# * FileName: stop.sh
# * Author  : ghostwwl
# * Date    : 2013.7.10
# * Note    : 停止服务器上相关服务
# * ***************************************************/


echo "Do you want to stop service[yes/no]?"
read answer
case "${answer}" in
	yes|y|Yes|YES)
  		#-------------------do stop command------------------
		# stop nginx
		NginxNumber=`ps -ef |grep nginx|grep -v 'grep'|wc -l`
		if [ $NginxNumber -gt 0 ]
		then
		    kill -15 `pgrep -f 'nginx\:\s*master'`
		fi

		# stop php-cgi
		PhpCgiNum=`ps -ef |grep php-fpm|grep -v 'grep'|wc -l`
		if [ $PhpCgiNum -gt 0 ]; then
		    # old php stop with php-fpm service
		    if [ -f /opt/php/sbin/php-fpm ]; then
		        /opt/php/sbin/php-fpm stop
		        printf "stop %-35s \033[32m%30s\033[0m\n" "[/opt/php]php-fpm use stop" "OK"
		    fi
		    # new server php stop with pid
		    if [ -f /opt/php/logs/php-fpm.pid ]; then
		        kill -15 `cat /opt/php/logs/php-fpm.pid`
		        printf "stop %-35s \033[32m%30s\033[0m\n" "[/opt/php]php-fpm" "OK"
		    fi
		    # old php stop with pid
		    if [ -f /usr/local/webserver/php/logs/php-fpm.pid ]; then
		        kill -15 `cat /usr/local/webserver/php/logs/php-fpm.pid`
		        printf "stop %-35s \033[32m%30s\033[0m\n" "[/usr/local/webserver/php]php-fpm" "OK"
		    fi
		    
		    # Force stop php ( unuse this only if can't stop php use normal way
		    #ps -ef|grep php|awk '{ print $2 }'|grep -v 'grep'|xargs kill -15
		    #if [ -f /opt/php/logs/php-fpm.pid ]; then
		    #    rm -f /opt/php/logs/php-fpm.pid
		    #fi
		    #if [ -f /usr/local/webserver/php/logs/php-fpm.pid ]; then
		    #    rm -f /usr/local/webserver/php/logs/php-fpm.pid
		    #fi
		fi

		# stop php run in command
		PhpNum=`ps -ef|grep -P 'php\s*?.*?\.php'|grep -v 'grep'|wc -l`
		if [ $PhpNum -gt 0 ]; then
		    ps -ef|grep -P 'php\s*?.*?\.php'|grep -v 'grep'|awk '{ print $2 }'|xargs kill -9
		    printf "stop %-35s \033[32m%30s\033[0m\n" "command php shell" "OK"
		fi

		# stop coreseek
		CoreseekNum=`ps -ef|grep -P 'searchd\s*?.*?\.conf'|grep -v 'grep'|wc -l`
		if [ $CoreseekNum -gt 0 ]; then
		    ps -ef|grep -P 'searchd\s*?.*?\.conf'|grep -v 'grep'|awk '{ print $2 }'|xargs kill -15
		    printf "stop %-35s \033[32m%30s\033[0m\n" "all coreseek searchd" "OK"
		fi

		# stop python
		PythonNum=`ps -ef|grep python|grep -v grep|wc -l`
		if [ $PythonNum -gt 0 ]; then
		    killall -15 python
		    printf "stop %-35s \033[32m%30s\033[0m\n" "all python" "OK"
		fi

		# stop ttserver
		TtNum=`ps -ef|grep ttserver|grep -v grep|wc -l`
		if [ $TtNum -gt 0 ]; then
		    ps aux|grep ttserver|awk '{ print $2 }'|xargs kill -15
		    printf "stop %-35s \033[32m%30s\033[0m\n" "all ttserver" "OK"
		fi

		# stop ktserver
		KtNum=`ps -ef|grep ktserver|grep -v grep|wc -l`
		if [ $KtNum -gt 0 ]; then
		    ps aux|grep ktserver|grep -v 'grep'|awk '{ print $2 }'|xargs kill -15
		    printf "stop %-35s \033[32m%30s\033[0m\n" "all ktserver" "OK"
		fi

		# stop httpsqs
		HttpsqsNum=`ps -ef|grep httpsqs|grep -v 'grep'|wc -l`
		if [ $HttpsqsNum -gt 0 ]; then
		    kill -15 `pgrep -f 'httpsqs\:\s*master process'`
		    printf "stop %-35s \033[32m%30s\033[0m\n" "all httpsqs service" "OK"
		fi

		# stop httpsqs
		HttpsqsNum=`ps -ef|grep rabbitmq-server|grep -v 'grep'|wc -l`
		if [ $HttpsqsNum -gt 0 ]; then
		    service rabbitmq-server stop
		    printf "stop %-35s \033[32m%30s\033[0m\n" "rabbitmq-server service" "OK"
		fi

		# stop mysql
		MysqlNum=`ps -ef|grep mysqld|grep -v grep|wc -l`
		if [ $MysqlNum -gt 0 ]; then
		    if [ -f /opt/mysql/3306/mysql ];then
		        /opt/mysql/3306/mysql stop
		        printf "stop %-35s \033[32m%30s\033[0m\n" "mysql" "OK"
		    fi
		    if [ -f /opt/mysql/mysql ]; then
		        /opt/mysql/mysql stop
		        printf "stop %-35s \033[32m%30s\033[0m\n" "mysql" "OK"
		    fi
		fi

		LamppNum=`ps -ef|grep lampp|grep -v grep|wc -l`
		if [ $LamppNum -gt 0 ]; then
		    if [ -f /opt/lampp/lampp ];then
		        /opt/lampp/lampp stop
		        printf "stop %-35s \033[32m%30s\033[0m\n" "lampp" "OK"
		    fi
		fi

		# stop jboss
		JbossNum=`ps -ef|grep -P 'java.*?jboss'|grep -v 'grep'|wc -l`
		if [ $JbossNum -gt 0 ]; then
		    killall java
		    printf "stop %-35s \033[32m%30s\033[0m\n" "jboss" "OK"
		fi
		#-------------------end stop command-----------------
		;;
	[nN]*)
  		echo "you chonice no"
		;;
	*)
  		echo "Sorry, ${answer} not recognized. Enter yes or no."
  		exit 1
		;;
	esac
		exit 0


