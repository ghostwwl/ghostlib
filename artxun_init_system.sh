#!/bin/sh
#/* ****************************************************
# * FileName: artxun_init_system.sh
# * Author  : ghostwwl
# * Date    : 2015
# * Note    : CentOS5 安装后的初始化
# * ***************************************************/

#***************************************************
# 安装时选最小化安装不要什么完整安装 这样会安装一堆没用的服务
#***************************************************


platform=`uname -i`
if [ $platform != "x86_64" ];then
    echo "only use in CentOs x86_64!"
    exit 1
fi



# 换163的元                                                                                                        
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget http://mirrors.163.com/.help/CentOS6-Base-163.repo -O /etc/yum.repos.d/CentOS-Base.repo


#添加rpmforge
rpm -Uvh  http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.2-2.el5.rf.x86_64.rpm
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag


# 安装常用开发库 
yum -y install gcc gcc-c++ autoconf libjpeg libjpeg-devel libpng libpng-devel \
freetype freetype-devel libxml2 libxml2-devel zlib zlib-devel glibc glibc-devel \
glib2 glib2-devel bzip2 bzip2-devel ncurses ncurses-devel curl curl-devel e2fsprogs \
e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel libtool \
libtool-libs libevent-devel libevent openldap openldap-devel nss_ldap openldap-clients \
openldap-servers libtool-ltdl libtool-ltdl-devel bison

# 装个libevent再说
yum -y install libevent-devel


# 自己看
yum clean all 
yum install kernel-devel kernel-headers && echo exclude=kernel* >> /etc/yum.conf
yum -y update glibc\*
yum -y update yum\* rpm\* python\*
yum -y update
# 加自动网络对时计划任务
yum -y install ntp 
echo "* 4 * * * /usr/sbin/ntpdate time.nist.gov > /dev/null 2>&1" >> /var/spool/cron/root
service crond restart

# 避免后面一些蛋疼
echo "ulimit -SHn 102400" >> /etc/rc.local
cat >> /etc/security/limits.conf << EOF
*           soft   nofile       65535
*           hard   nofile       65535
EOF

# ls 没有颜色不好看
cat >> /root/.bashrc << EOF
alias ls='ls --color'
EOF

/etc/init.d/iptables stop
/etc/init.d/ip6tables stop
/etc/init.d/sendmail stop
/etc/init.d/atd stop
/etc/rc.d/init.d/cups stop


mkdir /etc/cron.daily.bak
# 生成whatis的数据库我们也基本没用 每天多做 要死人的
mv /etc/cron.daily/makewhatis.cron /etc/cron.daily.bak
# 每天对磁盘上所有文件做本地数据库 我们基本们不用 
mv /etc/cron.daily/mlocate.cron /etc/cron.daily.bak

# 关掉蓝牙服务
chkconfig bluetooth off
chkconfig hidd off
# 关掉打印机服务
chkconfig cups off
#关掉iptables
chkconfig iptables off
# 关掉ip6的tables
chkconfig ip6tables off
# 关掉系统自动升级服务
chkconfig yum-updatesd off
# 关闭atd服务
chkconfig atd off
# 关闭sendmail 服务我们不做邮件服务器
chkconfig sendmail off
chkconfig isdn off


for sun in crond sshd network;do chkconfig --level 3 $sun on;done 


#disable selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

#set ssh
sed -i 's/^GSSAPIAuthentication yes$/GSSAPIAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
service sshd restart


#修改内核参数 优化系统性能
cat >> /etc/sysctl.conf << EOF
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1800
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_max_syn_backlog = 8192

net.core.netdev_max_backlog = 262144
net.core.somaxconn = 262144


#net.ipv4.tcp_mem = 94500000 915000000 927000000
#net.ipv4.tcp_max_orphans = 8192

#net.core.rmem_max = 16777216
#net.core.wmem_max = 16777216
#net.core.wmem_default = 8388608
#net.core.rmem_default = 8388608
EOF
/sbin/sysctl -p



#define the backspace button can erase the last character typed
echo 'stty erase ^H' >> /etc/profile

echo "syntax on" >> /root/.vimrc

#disable the ipv6
cat > /etc/modprobe.d/ipv6.conf << EOFI
alias net-pf-10 off
options ipv6 disable=1
EOFI

echo "NETWORKING_IPV6=off" >> /etc/sysconfig/network



