<?php
/* ****************************************************
 * FileName	: GKTserver.php
 * Author	: wule
 * Date		: 2013.5.31
 * Note		: inter face for Kyoto Tycoon
 * ***************************************************/
/*
------------ Kyoto Tycoon RPC Protocol------------
TSV-RPC

If a column includes one or more special characters such as tab, line-feed, and control characters, every column must be encoded by one of the following algorithms.

    Base64 encoding: colenc=B
    Quoted-printable: colenc=Q
    URL encoding: colenc=U

The encoding name must be described as an attribute of the value of the Content-Type header. The following is a typical request message with encoded TSV data.


/rpc/void
    Do nothing, just for testing.
    status code: 200.

/rpc/echo
    Echo back the input data as the output data, just for testing.
    input: (optional): arbitrary records.
    output: (optional): corresponding records to the input data.
    status code: 200.

/rpc/report
    Get the report of the server information.
    output: (optional): arbitrary records.
    status code: 200.

/rpc/play_script
    Call a procedure of the script language extension.
    input: name: the name of the procedure to call.
    input: (optional): arbitrary records whose keys trail the character "_".
    output: (optional): arbitrary keys which trail the character "_".
    status code: 200, 450 (arbitrary logical error).

/rpc/tune_replication
    Set the replication configuration.
    input: host: (optional): the name or the address of the master server. If it is omitted, replication is disabled.
    input: port: (optional): the port numger of the server. If it is omitted, the default port is specified.
    input: ts: (optional): the maximum time stamp of already read logs. If it is omitted, the current setting is not modified. If it is "now", the current time is specified.
    input: iv: (optional): the interval of each replication operation in milliseconds. If it is omitted, the current setting is not modified.
    status code: 200.

/rpc/status
    Get the miscellaneous status information of a database.
    input: DB: (optional): the database identifier.
    output: count: the number of records.
    output: size: the size of the database file.
    output: (optional): arbitrary records for other information.
    status code: 200.

/rpc/clear
    Remove all records in a database.
    input: DB: (optional): the database identifier.
    status code: 200.

/rpc/synchronize
    Synchronize updated contents with the file and the device.
    input: DB: (optional): the database identifier.
    input: hard: (optional): for physical synchronization with the device.
    input: command: (optional): the command name to process the database file.
    status code: 200, 450 (the postprocessing command failed).

/rpc/set
    Set the value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: value: the value of the record.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200.

/rpc/add
    Add a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: value: the value of the record.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200, 450 (existing record was detected).

/rpc/replace
    Replace the value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: value: the value of the record.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200, 450 (no record was corresponding).

/rpc/append
    Append the value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: value: the value of the record.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200.

/rpc/increment
    Add a number to the numeric integer value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: num: the additional number.
    input: orig: (optional): the origin number. If it is omitted, 0 is specified. "try" means INT64MIN. "set" means INT64MAX.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    output: num: the result value.
    status code: 200, 450 (the existing record was not compatible).

/rpc/increment_double
    Add a number to the numeric double value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: num: the additional number.
    input: orig: (optional): the origin number. If it is omitted, 0 is specified. "try" means negative infinity. "set" means positive infinity.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    output: num: the result value.
    status code: 200, 450 (the existing record was not compatible).

/rpc/cas
    Perform compare-and-swap.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    input: oval: (optional): the old value. If it is omittted, no record is meant.
    input: nval: (optional): the new value. If it is omittted, the record is removed.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200, 450 (the old value assumption was failed).

/rpc/remove
    Remove a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    status code: 200, 450 (no record was found).

/rpc/get
    Retrieve the value of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    output: value: (optional): the value of the record.
    output: xt: (optional): the absolute expiration time. If it is omitted, there is no expiration time.
    status code: 200, 450 (no record was found).

/rpc/check
    Check the existence of a record.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    output: vsiz: (optional): the size of the value of the record.
    output: xt: (optional): the absolute expiration time. If it is omitted, there is no expiration time.
    status code: 200, 450 (no record was found).

/rpc/seize
    Retrieve the value of a record and remove it atomically.
    input: DB: (optional): the database identifier.
    input: key: the key of the record.
    output: value: (optional): the value of the record.
    output: xt: (optional): the absolute expiration time. If it is omitted, there is no expiration time.
    status code: 200, 450 (no record was found).

/rpc/set_bulk
    Store records at once.
    input: DB: (optional): the database identifier.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    input: atomic: (optional): to perform all operations atomically. If it is omitted, non-atomic operations are performed.
    input: (optional): arbitrary records whose keys trail the character "_".
    output: num: the number of stored reocrds.
    status code: 200.

/rpc/remove_bulk
    Store records at once.
    input: DB: (optional): the database identifier.
    input: atomic: (optional): to perform all operations atomically. If it is omitted, non-atomic operations are performed.
    input: (optional): arbitrary keys which trail the character "_".
    output: num: the number of removed reocrds.
    status code: 200.

/rpc/get_bulk
    Retrieve records at once.
    input: DB: (optional): the database identifier.
    input: atomic: (optional): to perform all operations atomically. If it is omitted, non-atomic operations are performed.
    input: (optional): arbitrary keys which trail "_".
    output: num: the number of retrieved reocrds.
    output: (optional): arbitrary keys which trail the character "_".
    status code: 200.

/rpc/vacuum
    Scan the database and eliminate regions of expired records.
    input: DB: (optional): the database identifier.
    input: step: (optional): the number of steps. If it is omitted or not more than 0, the whole region is scanned.
    status code: 200.

/rpc/match_prefix
    Get keys matching a prefix string.
    input: DB: (optional): the database identifier.
    input: prefix: the prefix string.
    input: max: (optional): the maximum number to retrieve. If it is omitted or negative, no limit is specified.
    output: num: the number of retrieved keys.
    output: (optional): arbitrary keys which trail the character "_". Each value specifies the order of the key.
    status code: 200.

/rpc/match_regex
    Get keys matching a ragular expression string.
    input: DB: (optional): the database identifier.
    input: regex: the regular expression string.
    input: max: (optional): the maximum number to retrieve. If it is omitted or negative, no limit is specified.
    output: num: the number of retrieved keys.
    output: (optional): arbitrary keys which trail the character "_". Each value specifies the order of the key.
    status code: 200.

/rpc/match_similar
    Get keys similar to a string in terms of the levenshtein distance.
    input: DB: (optional): the database identifier.
    input: origin: the origin string.
    input: range: (optional): the maximum distance of keys to adopt. If it is omitted or negative, 1 is specified.
    input: utf: (optional): flag to treat keys as UTF-8 strings. If it is omitted, false is specified.
    input: max: (optional): the maximum number to retrieve. If it is omitted or negative, no limit is specified.
    output: num: the number of retrieved keys.
    output: (optional): arbitrary keys which trail the character "_". Each value specifies the order of the key.
    status code: 200.

/rpc/cur_jump
    Jump the cursor to the first record for forward scan.
    input: DB: (optional): the database identifier.
    input: CUR: the cursor identifier.
    input: key: (optional): the key of the destination record. If it is omitted, the first record is specified.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_jump_back
    Jump the cursor to a record for forward scan.
    input: DB: (optional): the database identifier.
    input: CUR: the cursor identifier.
    input: key: (optional): the key of the destination record. If it is omitted, the last record is specified.
    status code: 200, 450 (cursor is invalidated), 501 (not implemented).

/rpc/cur_step
    Step the cursor to the next record.
    input: CUR: the cursor identifier.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_step_back
    Step the cursor to the previous record.
    input: CUR: the cursor identifier.
    status code: 200, 450 (cursor is invalidated), 501 (not implemented).

/rpc/cur_set_value
    Set the value of the current record.
    input: CUR: the cursor identifier.
    input: value: the value of the record.
    input: step: (optional): to move the cursor to the next record. If it is omitted, the cursor stays at the current record.
    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_remove
    Remove the current record.
    input: CUR: the cursor identifier.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_get_key
    Get the key of the current record.
    input: CUR: the cursor identifier.
    input: step: (optional): to move the cursor to the next record. If it is omitted, the cursor stays at the current record.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_get_value
    Get the value of the current record.
    input: CUR: the cursor identifier.
    input: step: (optional): to move the cursor to the next record. If it is omitted, the cursor stays at the current record.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_get
    Get a pair of the key and the value of the current record.
    input: CUR: the cursor identifier.
    input: step: (optional): to move the cursor to the next record. If it is omitted, the cursor stays at the current record.
    output: xt: (optional): the absolute expiration time. If it is omitted, there is no expiration time.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_seize
    Get a pair of the key and the value of the current record and remove it atomically.
    input: CUR: the cursor identifier.
    output: xt: (optional): the absolute expiration time. If it is omitted, there is no expiration time.
    status code: 200, 450 (cursor is invalidated).

/rpc/cur_delete
    Delete a cursor implicitly.
    input: CUR: the cursor identifier.
    status code: 200, 450 (cursor is invalidated). 
    
*/



class KTserver
{
	protected $_host = null;
	protected $_port = null;
	protected $_timeout = 3; // 连接rpc接口或者http接口超时时间单位秒
	protected $_api_url = '';
	protected $_enctype = 2; // 0 serialize 1 json 2 原始字符串
	
	public $globs_name = null;
	protected $header;
	protected $mapload = false;
	protected $kt ;
	
	public function __construct($host='192.168.2.8', $port=8205, $glob_name='_KTSERVER_OBJ')
	{
		$this->KTserver($host, $port, $glob_name);
	}
	
	public function KTserver($host='localhost', $port=8205, $glob_name='_KTSERVER_OBJ')
	{
		if( $host ) $this->_host = $host;
		if( $port ) $this->_port = $port;
		$this->_api_url = "http://{$this->_host}:{$this->_port}/rpc/";
		$this->globs_name = $glob_name;
		$GLOBALS[$glob_name] = &$this;
	}
	
	protected function _encode( $value ) 
	{
		switch( $this->_enctype )
		{
			case 0:
				return serialize( $value );
				break;
			case 1:
				return json_encode( $value );
				break;
			default:
				return $value;
		}
	}
	
	protected function _decode( $value ) 
	{
		try{
			switch($this->_enctype)
			{
				case 0:
					return unserialize( $value );
					break;
				case 1:
					if( !empty( $value ) )$data = json_decode( $value, true );
					else $data = null;
					return (is_array($data)) ? $data : $value;
					break;
				default: 
					return $value;
			}
		}
		catch(Exception $e){
			return $value;
		}
	}
	
	protected function array2tsv(&$params)
	{
		$tsv = "";
		foreach($params as $key=>$value)
			$tsv .= base64_encode($key)."\t".base64_encode($value)."\n";
		return $tsv;
	}
	
	protected function &mapload(&$data, $colenc, $decode)
	{
		$rdata = array();
		if( preg_match('/lastid([0-9]*)[^0-9](.+)/', $data, $m1 ))
		{
			$rdata['lastid'] = $m1[1];
			if(preg_match('/value(.+)/', $m1[2], $m2 ))
				$rdata['value'] = $this->_decode( $m2[1] );
			unset($m1);
			unset($m2);
		}
		return $rdata;
	}
	
	protected function &tsv2array( &$response, $colenc='U', $decode=false )
	{
		if($response)
		{
			$data = array();
			$items = explode("\n",$response);
			foreach($items as &$item)
			{
				$kv = explode("\t", $item);
				if(count($kv) == 2)
				{
					if( $kv[0] == 'ERROR' ) $data['ERROR'] = $kv[1];
					else{
						$key = $kv[0];
						if ($kv[0]{0} == '_')  $key = substr($kv[0], 1);
						switch( $colenc ){
							case 'U':
								if($this->mapload) 
									$data[rawurldecode( $key )] = $this->mapload( rawurldecode($kv[1]), $colenc, $decode );
								else $data[rawurldecode( $key ) ]= rawurldecode($kv[1]);
								break;
							case 'B':
								$key = base64_decode( $key );
								if ($key{0} == '_')  $key = substr($key, 1);
								if($this->mapload) 
									$data[$key] = $this->mapload( base64_decode($kv[1]), $colenc, $decode );
								else $data[ $key ]= base64_decode($kv[1]);
								break;
							default:
								$data[ $key ]= $kv[1];
								break;
						}
						if( 'value'== $key || $decode ) $data[ $key ] = $this->_decode( $data[ $key ] );
					}
				}
			}
			unset($items);
			return $data;
		}
		return false;
	}


//	protected function interface_get($api, $data)
//	{
//		$api .='?';
//		$api .= http_build_query($data);
//		unset($data);
//		$ch = curl_init($api);
//		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
//		curl_setopt($ch, CURLOPT_HEADER, false);
//		curl_setopt($ch, CURLOPT_HEADERFUNCTION ,array($this, 'checkHeader' ));
//		$this->header='';
//		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $this->_timeout );
//		curl_setopt($ch, CURLOPT_TIMEOUT, $this->_timeout);
//		$response = curl_exec($ch);
//		curl_close($ch);
//		if($response){
//			$colenc = 'Q';
//			if( preg_match('/colenc=(U|B)/',$this->header,$m )) $colenc=$m[1];
//			return $this->tsv2array( $response, $colenc );
//		}
//		return false;
//	}
	
//	protected function checkHeader( $ch, $header )
//	{
//		$this->header .= $header;
//		return strlen($header);
//	}

	public function File_Write($filename, $filecode, $filemode)
	{
		$handle = @fopen($filename, $filemode);
		$key = @fwrite($handle, $filecode);
		if (!$key)
		{
			@chmod($filename, 0666);
			$key = @fwrite($handle, $filecode);
		}
		@fclose($handle);
		return $key;
	}
	
	protected function interface_post($api, &$data, $decode=false )
	{
		$matches = parse_url($api);
		$domain = $matches['host'];
		$uri = $matches['path'] ? $matches['path'].($matches['query'] ? '?'.$matches['query'] : '') : '/';
		$port = !empty($matches['port']) ? $matches['port'] : 80;
		$fp = fsockopen( $domain , $port );
		if (!$fp) return false;
		else {
			$data = $this->array2tsv($data);
			$request = "POST {$uri} HTTP/1.0\r\n";
			$request .= "Content-Type: text/tab-separated-values; colenc=B\r\n";
			$request .= "Content-length: ".strlen($data)."\r\n";
			$request .= "\r\n";
			$request .= $data;
			fwrite($fp, $request);
			stream_set_timeout($fp, $this->_timeout);
			$res = '';
			while (!feof($fp)) $res .= fgets($fp, 128);
			$info = stream_get_meta_data($fp);
			fclose($fp);
			if ($info['timed_out']) return false;
			else {
				if($res)
				{
					list($header, $body) = explode("\r\n\r\n", $res);
					if( preg_match('/HTTP\/1.1 ([0-9]+)/', $header, $m ))
					{
						$code = $m[1];
						if( $code == 200 || $code == 450 )
						{
							if( $body ){
								$colenc = 'Q';
								if( preg_match('/colenc=(U|B)/',$header,$m ))
									$colenc=$m[1];
								return $this->tsv2array( $body, $colenc, $decode );
							}
							return true;
						}
					}
				}
			}
		}
		return false;
	}
	
	// 运行脚本 这个我们基本不会用到
	public function play_script($name, $inmap)
	{
		$api = "{$this->_api_url}play_script";
		$params = array('name'=>$name);
		foreach($inmap as $k=>$v)
		{
			if( $k == 'value' ) $params['_'.$k] = $this->_encode($v);
			else $params['_'.$k] = $v;
		}
		return $this->interface_post($api, $params);
	}
	
	// 检查key是否存在 如果存在返回过期时间和值的大小
	public function check($key, $db=null)
	{
		$api = "{$this->_api_url}check";
		if(is_string($key)) $params = array('key' =>$key );
		else return false;
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params);
	}

	// 批量获取 传入参数 array(key1, key2,...,keyn)
	public function get_bulk(&$keys,$db=null,$decode=true)
	{
		$api = "{$this->_api_url}get_bulk";
		if(is_array($keys)) foreach($keys as $k) $params['_'.$k] = '';
		else return false;
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params, $decode);
	}
	
	// 根据key获取单挑数据
	public function get($key,$db=null)
	{
		$api = "{$this->_api_url}get";
		if(is_string($key)) $params = array('key' =>$key );
		else return false;
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params);
	}
	
	// 删除一条记录 
	public function remove($key,$db=null)
	{
		$api = "{$this->_api_url}remove";
		if(is_string($key)) $params = array('key' => $key );
		else return false;
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params);
	}

	// 批量删除记录 传入参数 array(key1, key2,...,keyn)
	public function remove_bulk(&$keys, $db=null, $decode=true)
	{
		$api = "{$this->_api_url}remove_bulk";
		if(is_array($keys)) foreach($keys as $k) $params['_'.$k] = '';
		else return false;
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params, $decode);
	}
	
	// 设置一个记录 key 键值 value 值 limittime 过期时间 单位秒
	public function set($key, $value, $limittime=0, $db=null)
	{
		$api = "{$this->_api_url}set";
		$value = $this->_encode( $value );
		$params = array('key'=>$key, 'value'=>$value );
		if($db) $params['DB']=$db;
		if ($limittime > 0) $params['xt'] = $limittime;
		return $this->interface_post($api, $params);
	}
	
	// 批量写入记录 参数 keys  如 array('key1'=>value1, 'key2'=>value2,...,'keyn'=>'valuen')
	public function set_bulk(&$keys, $limittime=0, $db=null)
	{
		$api = "{$this->_api_url}set_bulk";
		if(is_array($keys)) foreach($keys as $k=>$v) $params['_'.$k] = $this->_encode($v);
		else return false;
		if($db) $params['DB']=$db;
		if ($limittime > 0) $params['xt'] = $limittime;
		return $this->interface_post($api, $params);
	}
	
	// 根据正则查找 符合条件的key 这个千万不要随便使用 如果正则出问题可能造成ktserver大负载
	public function match_regex($regex_str, $max_num=10, $db=null)
	{
		$api = "{$this->_api_url}match_regex";
		$value = $this->_encode( $value );
		$params = array('regex'=>$regex_str, 'max'=>$max_num );
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params);
	}
	
	// 根据key的前缀获取
	public function match_prefix($key_prefix, $max_num=10, $db=null)
	{
		$api = "{$this->_api_url}match_prefix";
		$value = $this->_encode( $value );
		$params = array('regex'=>$key_prefix, 'max'=>$max_num );
		if($db) $params['DB']=$db;
		return $this->interface_post($api, $params);
	}
	
	public function increment($key, $num, $limittime=0, $db=null)
	{
		if (!is_numeric($num)) return false;
		$api = "{$this->_api_url}increment";
		$params = array('key'=>$key, 'num'=>$num);
		if ($db) $params['DB'] = $db;
		if ($limittime > 0) $params['xt'] = $limittime;
		$url = "{$api}?".http_build_query($params);
//		echo $url;
		return $this->interface_post($api, $params);
	}
	
	
//    /rpc/increment
//    Add a number to the numeric integer value of a record.
//    input: DB: (optional): the database identifier.
//    input: key: the key of the record.
//    input: num: the additional number.
//    input: orig: (optional): the origin number. If it is omitted, 0 is specified. "try" means INT64MIN. "set" means INT64MAX.
//    input: xt: (optional): the expiration time from now in seconds. If it is negative, the absolute value is treated as the epoch time. If it is omitted, no expiration time is specified.
//    output: num: the result value.
//    status code: 200, 450 (the existing record was not compatible). 
	
	public function http_fget2($url, $limit = 500000)
	{
		$response = '';
		$header_str = '';
		$matches = parse_url($url);
		$host = $matches['host'];
		$path = $matches['path'] ? $matches['path'].($matches['query'] ? '?'.$matches['query'] : '') : '/';
		$port = !empty($matches['port']) ? $matches['port'] : 80;

		$out = "GET {$path} HTTP/1.0\r\n";
		$out .= "Accept: */*\r\n";
		$out .= "Accept-Language: zh-cn\r\n";
		$out .= "User-Agent: {$_SERVER[HTTP_USER_AGENT]}\r\n";
		$out .= "Host: {$host}\r\n";
		$out .= "Connection: Close\r\n";
		$out .= "\r\n";
		
		$fp = @fsockopen(($ip ? $ip : $host), $port, $errno, $errstr, $this->_timeout);
		if(!$fp) return '';
		else{
			stream_set_blocking($fp, true);
			stream_set_timeout($fp, $this->_timeout);
			@fwrite($fp, $out);
			$status = stream_get_meta_data($fp);
			if(!$status['timed_out'])
			{
				while (!feof($fp))
				{
					if(($header = @fgets($fp)) && ($header == "\r\n" ||  $header == "\n")) break;
					$header_str .= $header;
				}

				$stop = false;
				while(!feof($fp) && !$stop)
				{
					$data = fread($fp, ($limit == 0 || $limit > 8192 ? 8192 : $limit));
					$response .= $data;
					if($limit)
					{
						$limit -= strlen($data);
						$stop = $limit <= 0;
					}
				}
			}
			@fclose($fp);
			return $response;
			if( preg_match('/HTTP\/1.1 ([0-9]+)/', $header_str, $m ))
			{
				$code = $m[1];
				if($code == 200 ||  $code == 200)
				{
					if( $body ){
						$colenc = 'Q';
						if( preg_match('/colenc=(U|B)/',$header_str,$m ))
						$colenc=$m[1];
						return $this->tsv2array( $response, $colenc, $decode );
					}
					return true;
				}
			}
			return false;
		}
	}
	
	// 不走rpc的单条获取
	public function get2($cachekey)
	{
		$get_api_url = "http://{$this->_host}:{$this->_port}/".rawurldecode($cachekey);
		$result = $this->http_fget2($get_api_url);
		if (!empty($result)) return $result;
		return '';
	}
	
	public function check_system()
	{
		$n = 'check_system';
		$ret = 0;
		if( $this->set( $n, time() ) ) $ret += 1;
		if( $this->get( $n ) ) $ret += 2;
		return $ret;
	}
	
	// 服务器状态信息报告
	public function &server_report()
	{
		$api = $this->_api_url.'report';
		$info = $this->interface_post($api, array());
		$info['db_total_size'] = $this->file_size($info['db_total_size']);
		unset($result);
		return $info;
	}
	
	// 获取服务器信息
	public function &get_serverinfo()
	{
		$api = $this->_api_url.'status';
		$info = $this->interface_post($api, array());
		$info['size'] = $this->file_size($info['size']);
		$info['msiz'] = $this->file_size($info['msiz']);
		$info['realsize'] = $this->file_size($info['realsize']);
		unset($result);
		return $info;
	}
	
	public function file_size($size) 
	{ 
		if($size > 1073741824) $size = round($size / 1073741824 * 100) / 100 . ' G'; 
		elseif($size > 1048576) $size = round($size / 1048576 * 100) / 100 . ' M'; 
		elseif($size > 1024) $size = round($size / 1024 * 100) / 100 . ' K'; 
		else $size = $size . ' B'; 
		return $size; 
	}
}

// Class_Ttserver用来替代老的ttserver重载
class Class_Ttserver extends  KTserver 
{
	public function __construct($host, $port, $glob_name='__search_cacheobj')
	{
		parent::__construct($host, $port, '__search_cacheobj');
	}
	
	public function Class_Ttserver($host, $port, $glob_name='__search_cacheobj')
	{
		parent::__construct($host, $port, '__search_cacheobj');
	}
	
	
	public function set_cache($cachekey, $cachevar, $limittime=0)
	{
		return $this->set($cachekey, $cachevar, $limittime);
	}
	
	public function get_cache($cachekey)
	{
		return $this->get2($cachekey);
	}
	
	public function del_cache($cachekey)
	{
		$this->remove($cachekey);
	}
}


function test()
{
	$st = microtime(true);
	$t = new Class_Ttserver('192.168.2.xxx', 8205);
	//$mm = array();
	//for($i = 0; $i<100;$i++){
	//	$mm[$i] = "$i{$txt}";
	//}
	//
	//$d = $t->set_bulk($mm, 3600);
	//
	//$d = $t->get_bulk(array(1,2,3,4,5,6,7,8,9,10));
	//$c = $t->set("wz", $txt, 6000);
	//$d = $t->set('123', 'asdfasdfasdf', 'ecm_s');
	//$d = $t->get(123);
	//$d = $GLOBALS['_KTSERVER_OBJ']->get('123213');
	//$t->remove("wz");
	//$d = $t ->get('__paimai_salerinfo_120924');
	//$d = $t ->check('wz');
	//$d = $t ->get('0');
	//var_dump($t->increment('10', 1000));
	
	//$d = $t ->check('__paimai_salerinfo_120924');
	//$d = $t->remove_bulk(array('wz', 'wz1'));
	//$d = $t->get_bulk(array('__paimai_salerinfo_120924'));
	
	//$d = $t->match_regex('^__paimai_salerinfo_.*$', 100);
      //$d = $t->match_prefix('__paimai_salerinfo_', 10);
	//$d = $t->get_cache('__paimai_salerinfo_456075');
	//$d = $t->get_cache('123');
	echo microtime(true) - $st;
	print_r($d);
	//$m= $t->get_serverinfo();
	//print_r($m);
	//$m= $t->server_report();
	//print_r($m);
}


function test_mutil_db()
{
	$T = new KTserver('192.168.2.xxx', 11205, 'test_mutil_db');
//	$d = $T->match_regex('^ecm_member_[0-9]+$', 100);
	$d = $T->get('ecm_goods_82023');
//	$d = $T->get_bulk($gets);
	$d['value'] = unserialize($d['value']);
//	$d = $T->match_prefix('a', 100);
	print_r($d);
	exit();
	$db = new Class_Mysql('192.168.xx.x', 'xxxx', '****,(***', 'xxxxxx', '', true);
	$max_id = 637830;
	
	while (1){
		$sql = "select a.*, b.province, b.city, b.is_realname_auth as auth_realname, b.is_mobile_auth as auth_mobile, b.is_email_auth as auth_email from ecm_member a left join ecm_c2c_member b on a.user_id=b.user_id where a.user_id>{$max_id} order by a.user_id asc limit 100;";
		$db->Execute('wslist', $sql);
		$rds = array();
		while($row = $db->GetArray('wslist')){
			$rds["ecm_member_{$row['user_id']}"] = serialize($row);
//			print_r($row);
//			exit();
			$max_id = max($max_id, $row['user_id']);
		}
//		break;
		$db->FreeResult("wslist");
		
		$d = $T->set_bulk($rds, 0);
		echo "max_id {$max_id}";
		echo "\t\tinsert {$d['num']} OK\n";
		if (!$rds) break;
	}
	$db->Close();
	
	
	
	
}
set_time_limit(0);
// test_mutil_db();
test();
?>
