<?php
/*****************************************
 * FileName	: redis_session.php
 * Author	: ghostwwl@gmail.com
 * Note		:
 * History  :
 *****************************************/


class RedisSession
{
	private $_redis = null;
	public $max_life_time = 86400; // session 过期时间
	public $session_cookie_path = '/';
	public $session_cookie_domain = '';
	public $session_cookie_secure = false;
	public $session_name = 'ONXID';
	public $_ip = '';

	public function __construct(array $redis_config, $session_name = 'ONXID', $session_id='')
	{
		if ($this->_redis === null){
			$this->_redis = new Redis();
		}
		$connect_flag = $this->_redis->connect($redis_config['host'], $redis_config['port']);
		if (!$connect_flag){
			throw new Exception('connect redis failed.');
		}
		if (!empty($redis_config['password'])){
			$auth_flag = $this->_redis->auth($redis_config['password']);
			if (!$auth_flag){
				throw new Exception('session redis auth failed.');
			}
		}

		session_set_save_handler(
			array (& $this, '_session_open'),   //在运行session_start()时执行
			array (& $this, '_session_close'),  //在脚本执行完成或调用session_write_close() 或 session_destroy()时被执行,即在所有session操作完后被执行
			array (& $this, '_session_read'),   //在运行session_start()时执行,因为在session_start时,会去read当前session数据
			array (& $this, '_session_write'),  //此方法在脚本结束和使用session_write_close()强制提交SESSION数据时执行
			array (& $this, '_session_destroy'),  //在运行session_destroy()时执行
			array (& $this, '_session_gc')     //执行概率由session.gc_probability 和 session.gc_divisor的值决定,时机是在open,read之后,session_start会相继执行open,read和gc
		);
		register_shutdown_function('session_write_close');

		// 如果要不是当前域名或者有二级域名撒的
		//$this->session_cookie_path = '';
		//$this->session_cookie_domain = '';
		$this->session_cookie_secure = false;
		$this->session_name = $session_name;
		$this->_ip = $this->real_ip();

		// 处理session id
		if ($session_id == '' && !empty($_COOKIE[$this->session_name])){
			$this->session_id = $_COOKIE[$this->session_name];
		}
		else $this->session_id = $session_id;

		if ($this->session_id){
			// 验证session_id
			$tmp_session_id = substr($this->session_id, 0, 32);
			if ($this->gen_session_key($tmp_session_id) == substr($this->session_id, 32)){
				$this->session_id = $tmp_session_id;
			}
			else $this->session_id = '';
		}

		if (!$this->session_id){
			$this->gen_session_id();
			session_id(sprintf('%s%s', $this->session_id, $this->gen_session_key($this->session_id)));
		}
	}

	public function real_ip()
	{
		static $realip = NULL;
		if ($realip !== NULL) return $realip;

		if (isset($_SERVER))
		{
			if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])){
				$arr = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
				/* 取X-Forwarded-For中第一个非unknown的有效IP字符串 */
				foreach ($arr AS $ip){
					$ip = trim($ip);
					if ($ip != 'unknown'){
						$realip = $ip;
						break;
					}
				}
			}
			elseif (isset($_SERVER['HTTP_CLIENT_IP'])){
				$realip = $_SERVER['HTTP_CLIENT_IP'];
			}
			else if (isset($_SERVER['REMOTE_ADDR'])){
				$realip = $_SERVER['REMOTE_ADDR'];
			}
			else $realip = '0.0.0.0';
		}
		else
		{
			if (getenv('HTTP_X_FORWARDED_FOR')) $realip = getenv('HTTP_X_FORWARDED_FOR');
			elseif (getenv('HTTP_CLIENT_IP')) $realip = getenv('HTTP_CLIENT_IP');
			else $realip = getenv('REMOTE_ADDR');
		}

		preg_match("/[\d\.]{7,15}/", $realip, $onlineip);
		$realip = !empty($onlineip[0]) ? $onlineip[0] : '0.0.0.0';

		return $realip;
	}

	/**
	 * open session handler
	 * @param string $save_path
	 * @param string $session_name
	 * @return boolen
	 */
	public function _session_open($save_path, $session_name)
	{
		return true;
	}

	/**
	 * read session handler
	 * @param string $sesskey
	 * @return string
	 */
	public function _session_read($sesskey)
	{
		$data = $this->_redis->get($this->session_id);
		if (false === $data)
		{
			$this->insert_session();
			return '';
		}
		else
		{
			// 这里可以考虑 给当前活动的$this->session_id 延长ttl
			// 这样可以变向实现某个用户多久没有活动就自动 丢失
			return $data;
		}
	}

	/**
	 * write session handler
	 * @param stirng $sesskey
	 * @param string $sessvalue
	 * @return boolen
	 */
	public function _session_write($sesskey, $sessvalue)
	{
		return $this->_redis->setex($this->session_id, $this->max_life_time, $sessvalue);
	}

	/**
	 * close session handler
	 * @return boolen
	 */
	public function _session_close()
	{
		return true;
	}

	/**
	 * destory session handler
	 * @param stirng $sesskey
	 * @return void
	 */
	public function _session_destroy($sesskey)
	{
		$this->destroy_session();
	}

	/**
	 * gc session handler 清除过期session
	 * @param int $maxlifetime
	 * @return boolen
	 */
	public function _session_gc($maxlifetime)
	{
		return true;
	}

	/**
	 * 生成session id
	 * @return string
	 */
	public function gen_session_id()
	{
		$this->session_id = md5(uniqid(mt_rand(), true));

		return $this->insert_session();
	}

	/**
	 * 生成session验证串
	 * @param string $session_id
	 * @return stirng
	 */
	public function gen_session_key($session_id)
	{
		static $ip = '';

		if ($ip == '')
		{
			$ip = substr($this->_ip, 0, strrpos($this->_ip, '.'));
		}

		return sprintf('%08x', crc32(!empty($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] . ROOT_PATH . $ip . $session_id : ROOT_PATH . $ip . $session_id));
	}

	/**
	 * 插入一个新session
	 * @return void
	 */
	public function insert_session()
	{
		$result = $this->_redis->setex($this->session_id, $this->max_life_time, '');
		if ($result === false)
		{
			//exit('Data Cannot be written on memcached');
			$html = <<<SESSERR
	        <!doctype html>
			<html>
				<head>
				<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
				<meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0;" name="viewport" />
				<meta content="yes" name="apple-mobile-web-app-capable" />
				<meta content="black" name="apple-mobile-web-app-status-bar-style" />
				<title></title>
				</head>
			<body>
			<div>
			    <p style="width:100%;line-height:3rem;color:#666;font-size:1.2rem;text-align:center; margin-top:35%;">服务器繁忙，请刷新重试！</p>
			    <a style="width:43%;line-height:2.6rem;color:#fff;font-size:1.2rem;text-align:center;border-radius:5px;display:block;text-decoration:none;background-color:#ff4060;margin:0 auto;" href="javascript:window.location.reload();">刷新</a>
			</div>
			</body>
			</html>
SESSERR;
			echo $html;
			exit();
		}
	}

	/**
	 * 清除一个session
	 * @return boolen
	 */
	public function destroy_session()
	{
		$_SESSION = array();
		setcookie($this->session_name, $this->session_id, 1, $this->session_cookie_path, $this->session_cookie_domain, $this->session_cookie_secure);
		return $this->delete_session($this->session_id);
	}

	/**
	 * 删除指定ID的Session
	 * @param  string $session_id
	 * @return bool
	 **/
	public function delete_session($session_id)
	{
		return $this->_redis->del($session_id);
	}

	/**
	 * 获取当前session id
	 * @return string
	 */
	public function get_session_id()
	{
		return $this->session_id;
	}

	/**
	 * 获取用户数量
	 * @return int
	 */
	public function get_users_count()
	{
		return $this->_redis->dbSize();
	}

	/**
	 * 打开session
	 * @return void
	 */
	public function redis_session_start()
	{
		session_name($this->session_name);
		session_set_cookie_params($this->max_life_time, $this->session_cookie_path, $this->session_cookie_domain, $this->session_cookie_secure);
		return session_start();
	}
}


function rstest(){
	$session_conf = array(
		'host' => '127.0.0.1',
		'port' => 8205,
		'password' => 'wule123465',
	);

	print_r($_COOKIE);
	echo "<br>";
	$msession = new RedisSession($session_conf, 'XID');
	$msession->redis_session_start();
	echo $msession->get_session_id();
	echo "<br>";
	$_SESSION['last_opt_time'] = date('Y-m-d H:i:s');
	$_SESSION['haha'] = '好人';
	$_SESSION['session_name'] = $msession->session_name;
	echo "<br>";
	print_r($_SESSION);
	echo "<br>";
	print_r($msession->get_session_id());
	echo "<br>";
}

?>


