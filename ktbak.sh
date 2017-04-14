#!/bin/sh

ktroot="/usr/local/ktserver/bin"

if [ $# -lt 3 ]; then
	echo "UseAge: ktbak.sh dump xx.kch xx.snap | ktbak.sh load r.kch xx.snap"
	exit 0
fi

type=$1
src_kch=$2
dst_snap=$3

if [ $type = "dump" ]; then
	if [ -f $src_kch -a -n $dst_snap ]; then
		# 从ktserver 导出快照备份
		echo "do ${ktroot}/kttimedmgr dump -onl ${src_kch} ${dst_snap}"
		${ktroot}/kttimedmgr dump -onl ${src_kch} ${dst_snap}
	fi
elif [ $type = "load" ]; then
	if [ -n $src_kch -a -f $dst_snap ]; then
		# 从ktserver 快照生成kch数据库文件
		echo "do ${ktroot}/kttimedmgr load -onl ${src_kch} ${dst_snap}"
		${ktroot}/kttimedmgr load -onl ${src_kch} ${dst_snap}
	fi
else
	echo "UseAge: ktbak.sh dump xx.kch xx.snap | ktbak.sh load r.kch xx.snap"
fi
