<?php
/*****************************************
 * FileName : ArtxunSyncTask.php
 * Author   : ghostwwl@gmail.com
 * Note     : 使用rabbitmq 列 使用php默认AMQP绑定库
 * History  :
 *****************************************/



require_once('ArtxunBaseWallets.php');
require_once('ArtxunWalletsWithdraw.php');


/**
莫有办法 有的不能公开的 直接删掉 这只是展示一种思路

/*

class ArtxunWalletsTask
{
	private $amqp_config = [
		'host'            => _MESSAGE_SERVER,
		'port'            => _MESSAGE_PORT,
		'login'           => _MESSAGE_USER,
		'password'        => _MESSAGE_PWD,
		'vhost'           => _MESSAGE_VHOST,
		'connect_timeout' => 1,
	];

	private $task_sqs = [
		'ccallback_sqs'       => 'post_cbc',
		'wcallback_sqs'       => 'post_wbc',
		'check_corder_sqs'    => 'check_corder',
		'check_worder_sqs'    => 'check_worder',
		'sms_sqs'             => 'send_sms',
		'wallets_log'         => 'log',
		'scheduled_tasks_sqs' => 'crontab',
	];

	private $task_config_map = [
		1 => [
			'TaskName'       => '充值异步回调通知接入方',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'ccallback_sqs',
			'RouteKey'       => 'post_cbc',
			'ProcessHandler' => 'do_ccallback_sqs_handler',
			'HasDLX'         => false,
		],
		2 => [
			'TaskName'       => '提现异步回调通知接入方',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'wcallback_sqs',
			'RouteKey'       => 'post_wbc',
			'ProcessHandler' => 'do_wcallback_sqs_handler',
			'HasDLX'         => false,
		],
		3 => [
			'TaskName'       => '检查充值订单是否到账',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'check_corder_sqs',
			'RouteKey'       => 'check_corder',
			'ProcessHandler' => 'do_check_corder_sqs_handler',
			'HasDLX'         => false,
		],
		4 => [
			'TaskName'       => '检查提现打款是否到账',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'check_worder_sqs',
			'RouteKey'       => 'check_worder',
			'ProcessHandler' => 'do_check_worder_sqs_handler',
			'HasDLX'         => false,
		],
		5 => [
			'TaskName'       => '发送短信',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'sms_sqs',
			'RouteKey'       => 'send_sms',
			'ProcessHandler' => 'do_sms_sqs_handler',
			'HasDLX'         => false,
		],
		6 => [
			'TaskName'       => '系统日志处理',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'wallets_log',
			'RouteKey'       => 'log',
			'ProcessHandler' => 'do_wallets_log_handler',
			'HasDLX'         => false,
		],
		7 => [
			'TaskName'       => '通用计划任务调度',
			'Exchange'       => _MESSAGE_TASK_EXCHANGE,
			'Queue'          => 'scheduled_tasks_sqs',
			'RouteKey'       => 'crontab',
			'ProcessHandler' => 'do_scheduled_tasks_sqs_handler',
			'HasDLX'         => false,
		],
	];

	private $amqp_conn = null;

	public function __construct()
	{

	}

	/**
	 * 获取 AMQP 连接
	 * @return AMQPConnection|null
	 * @throws Exception
	 */
	protected function getAmqpConnect()
	{
		if (!is_null($this->amqp_conn))
		{
			if ($this->amqp_conn->isConnected()) {
				return $this->amqp_conn;
			}
		}

		$this->amqp_conn = new AMQPConnection($this->amqp_config);
		if (!$this->amqp_conn->connect()) {
			throw new \Exception('连接消息服务器失败');
		}

		return $this->amqp_conn;
	}

	/**
	 * 在消息服务器上创建 队列服务持久化层级结构
	 * @return bool
	 * @throws Exception
	 */
	public function init_aync_task_server()
	{
		//创建连接和[信道]channel
		$conn    = $this->getAmqpConnect();
		$channel = new AMQPChannel($conn);

		//创建交换机
		$exchange = new AMQPExchange($channel);
		$exchange->setName(_MESSAGE_TASK_EXCHANGE);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) {
			throw new Exception('初始化消息交换机失败');
		}

		foreach ($this->task_sqs as $queue_name => $route_key)
		{
			$$queue_name = new AMQPQueue($channel);
			$$queue_name->setName($queue_name);
			$$queue_name->setFlags(AMQP_DURABLE);
			$wait_process_msg_count = $$queue_name->declareQueue();
			//echo "{$queue_name}待处理消息量:{$wait_process_msg_count}\n";
			// 绑定消息交换机路由
			$$queue_name->bind(_MESSAGE_TASK_EXCHANGE, $route_key);

			// ---------------创建对应的死信队列以便实现延时转发----------------
			$dlxqueue = new AMQPQueue($channel);
			$dlxqueue->setName("delay_{$queue_name}");
			$dlxqueue->setArgument('x-dead-letter-exchange', _MESSAGE_TASK_EXCHANGE);
			$dlxqueue->setArgument('x-dead-letter-routing-key', $route_key);
			$dlxqueue->setFlags(AMQP_DURABLE);
			$wait_process_msg_count = $dlxqueue->declareQueue();
			// 绑定消息交换机路由
			$dlxqueue->bind(_MESSAGE_TASK_EXCHANGE, "delay_{$route_key}");
		}

		// 创建财务日志交换机
		/*
		$exchange = new AMQPExchange($channel);
		$exchange->setName(_MESSAGE_LOG_EXCHANGE);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) throw new Exception('初始化交换机失败');

		$queue = new AMQPQueue($channel);
		$queue->setName('wallets_log');
		$queue->setFlags(AMQP_DURABLE);
		$queue->declareQueue();
		$queue->bind(_MESSAGE_LOG_EXCHANGE, 'log');


		$queue_dlx = new AMQPQueue($channel);
		$queue_dlx->setName('delay_wallets_log');
		$queue_dlx->setFlags(AMQP_DURABLE);
		$queue_dlx->setArgument('x-dead-letter-exchange', _MESSAGE_LOG_EXCHANGE);
		$queue_dlx->setArgument('x-dead-letter-routing-key', 'log');
		$queue_dlx->declareQueue();
		$queue_dlx->bind(_MESSAGE_LOG_EXCHANGE, 'delay_log');
		*/

		// 截获php error handler
		//set_error_handler(array(&$this, 'wallers_error_handler'));

		echo $this->message('----- 初始化RabbitMQ消息结构 OK -----');

		return true;
	}

	/**
	 * 删除所有持久队列结构及路由绑定 或 清除某队列所有消息
	 * @param int $do_type 1 delete 2 purge
	 * @return bool
	 * @throws Exception
	 */
	public function OperateAllQueue($do_type = 1)
	{
		if ($do_type !== 1 && $do_type !== 2) {
			throw new \Exception('错误的操作参数');
		}

		$conn    = $this->getAmqpConnect();
		$channel = new AMQPChannel($conn);

		$exchange = new AMQPExchange($channel);
		$exchange->setName(_MESSAGE_TASK_EXCHANGE);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) {
			throw new Exception('初始化交换机失败');
		}

		foreach ($this->task_sqs as $queue_name => $route_key)
		{
			$$queue_name = new AMQPQueue($channel);
			$$queue_name->setName($queue_name);
			$$queue_name->setFlags(AMQP_DURABLE);
			$wait_process_msg_count = $$queue_name->declareQueue();
			switch ($do_type) {
				case 1:
					$$queue_name->delete();
					break;
				case 2:
					$$queue_name->purge();
					break;
			}

			// ---------------创建对应的死信队列----------------
			$dlxqueue = new AMQPQueue($channel);
			$dlxqueue->setName("delay_{$queue_name}");
			$dlxqueue->setArgument('x-dead-letter-exchange', _MESSAGE_TASK_EXCHANGE);
			$dlxqueue->setArgument('x-dead-letter-routing-key', $route_key);
			$dlxqueue->setFlags(AMQP_DURABLE);
			$wait_process_msg_count = $dlxqueue->declareQueue();
			switch ($do_type) {
				case 1:
					$dlxqueue->delete();
					break;
				case 2:
					$dlxqueue->purge();
					break;
			}
		}

		if ($do_type < 2) {
			echo $this->message('----- 删除所有消息队列 OK -----');
		}
		else {
			echo $this->message('----- 清除所有队列里的消息 OK -----');
		}

		return true;
	}

	/**
	 * 异步任务处理入口
	 * @param $type
	 * @throws Exception
	 */
	public function processEntry($type)
	{
		if (!isset($this->task_config_map[$type])) {
			throw new \Exception('未知的任务类型');
		}

		$task_config = $this->task_config_map[$type];

		print_r($task_config);

		//创建连接和[信道]channel
		$conn    = $this->getAmqpConnect();
		$channel = new AMQPChannel($conn);

		// 一个连接理论上可以创建N个信道 信道是基于TCP链接的
		// 创建和销毁比tcp连接代价小很多

		// 创建异步回调任务交换机
		$exchange = new AMQPExchange($channel);
		$exchange->setName($task_config['Exchange']);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) {
			throw new Exception('初始化交换机失败');
		}

		$queue = new AMQPQueue($channel);
		$queue->setName($task_config['Queue']);
		$queue->setFlags(AMQP_DURABLE);
		// 如果此任务队列绑定有死信路由
		if ($task_config['HasDLX']) {
			$queue->setArgument('x-dead-letter-exchange', $task_config['Exchange']);
			$queue->setArgument('x-dead-letter-routing-key', $task_config['RouteKey']);
		}
		$queue->declareQueue();
		$queue->bind($task_config['Exchange'], $task_config['HasDLX'] ? "delay_{$task_config['RouteKey']}" :
			                                     $task_config['RouteKey']
		);

		//阻塞模式接收消息
		echo $this->message(sprintf('开始 %s(%s) 处理器%s', $task_config['TaskName'], $task_config['ProcessHandler'], PHP_EOL));

		$GLOBALS['AsyncTaskConfig']  = $task_config;
		$GLOBALS['AsyncExchangeObj'] = $exchange;

		$channel->qos(0, 1);

		$queue->consume(array($this, $task_config['ProcessHandler']));

		if (!$conn->disconnect()) {
			throw new Exception('断开链接失败');
		}
	}

	/**
	 * @param $route_key    路由key[post_cbc, post_wbc, check_corder, check_worder, send_sms, log, crontab]
	 * @param $msg_json_obj
	 * @param null $expir 消息过期时间(单位秒) 到了时间未处理 自动删除
	 * @param null $msg_type 消息头里指定type
	 * @return bool
	 * @throws Exception
	 */
	public function add_msg($route_key, $msg_json_obj, $expir = null, $msg_type = null)
	{
		//创建连接和channel
		$conn = $this->getAmqpConnect();

		$channel  = new AMQPChannel($conn);
		$exchange = new AMQPExchange($channel);

		//if ($route_key == 'log') $exchange->setName(_MESSAGE_LOG_EXCHANGE);
		//else $exchange->setName(_MESSAGE_TASK_EXCHANGE);

		$exchange->setName(_MESSAGE_TASK_EXCHANGE);

		$msg_cfg = [
			'content_encoding' => 'utf-8',
			'timestamp'        => time(),
			'delivery_mode'    => '2',
			//'message_id'     => '',
			//'correlation_id' => '',
			//'reply_to'       => '',   // 一般为回复的route_key
		];

		if (!is_null($msg_type)) {
			$msg_cfg['type'] = $msg_type;
		}

		if (is_numeric($expir)) {
			$msg_cfg['expiration'] = $expir * 1000;
			$route_key             = "delay_{$route_key}";
		}

		// 开始[发布消息]事务
		$channel->startTransaction();
		try {
			if (1 == $exchange->publish($msg_json_obj, $route_key, AMQP_MANDATORY, $msg_cfg)) {
				return $channel->commitTransaction();
			}
			else {
				$channel->rollbackTransaction();
			}
		}
		catch (Exception $m) {
			$channel->rollbackTransaction();
			throw new \Exception($m->getMessage());
		}
		$conn->disconnect();

		return false;
	}

	/**
	 * 从某个交换机的某个持久队列(非死信)中 根据消息内容 查找首条符合条件消息 并返回
	 * @param $exchange_name
	 * @param $queue_name
	 * @param $search_k         json消息里的要查找的key
	 * @param $search_v         json消息里的要查找的value
	 * @param bool $do_act 找到消息是否对找到的消息act
	 * @return null
	 * @throws Exception
	 */
	public function searchMessage($exchange_name, $queue_name, $search_k, $search_v, $do_act = true)
	{
		//创建连接和[信道]channel
		$conn    = $this->getAmqpConnect();
		$channel = new AMQPChannel($conn);

		// 一个连接理论上可以创建N个信道 信道是基于TCP链接的
		// 创建和销毁比tcp连接代价小很多

		// 创建异步回调任务交换机
		$exchange = new AMQPExchange($channel);
		$exchange->setName($exchange_name);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) {
			throw new Exception('初始化交换机失败');
		}

		$queue = new AMQPQueue($channel);
		$queue->setName($queue_name);
		$queue->setFlags(AMQP_DURABLE);
		$wait_process_message_count = $queue->declareQueue();

		$result = null;
		while (1)
		{
			$msg_obj = $queue->get(AMQP_NOPARAM);
			if (!$msg_obj) break;
			$arr_obj = json_decode($msg_obj->getBody(), true);
			if ($arr_obj[$search_k] == $search_v) {
				$result = $msg_obj;
				if ($do_act) {
					$queue->ack($msg_obj->getDeliveryTag());
				}
				break;
			}
			unset($arr_obj);
		}
		$conn->disconnect();

		return $result;
	}

	/**
	 * @param $exchange_name
	 * @param $queue_name
	 * @param $search_k
	 * @param $search_v
	 * @param bool $do_act
	 */
	public function editMessage($exchange_name, $queue_name, $search_k, $search_v, $do_act = true)
	{

	}

	/**
	 * 遍历某个交换机下的某个持久队列(非死信队列)
	 * @param $exchange_name
	 * @param $queue_name
	 * @return array
	 * @throws Exception
	 */
	public function &TraversalMessage($exchange_name, $queue_name)
	{
		//创建连接和[信道]channel
		$conn    = $this->getAmqpConnect();
		$channel = new AMQPChannel($conn);

		// 一个连接理论上可以创建N个信道 信道是基于TCP链接的
		// 创建和销毁比tcp连接代价小很多

		// 创建异步回调任务交换机
		$exchange = new AMQPExchange($channel);
		$exchange->setName($exchange_name);
		$exchange->setType(AMQP_EX_TYPE_DIRECT);
		$exchange->setFlags(AMQP_DURABLE);
		$exchange->declareExchange();
		$init_flag = $exchange->declareExchange();
		if (!$init_flag) {
			throw new Exception('初始化交换机失败');
		}

		$queue = new AMQPQueue($channel);
		$queue->setName($queue_name);
		$queue->setFlags(AMQP_DURABLE);
		$wait_process_message_count = $queue->declareQueue();

		$undo_msg = [];

		for ($i = 0; $i < $wait_process_message_count; $i++)
		{
			$msg_obj = $queue->get(AMQP_NOPARAM);
			if (!$msg_obj) break;
			else {
				$undo_msg[$i] = $msg_obj;
			}
		}
		$conn->disconnect();

		return $undo_msg;
	}

	static function message($msg, $leve = 1)
	{
		$MSG_LEVE = [1 => 'INFO', 2 => 'WARNING', 3 => 'ERROR'];
		return sprintf("%-7s %s] %s%s", $MSG_LEVE[$leve], date('Y-m-d H:i:s'), $msg, PHP_EOL);
	}

	/**
	 *
	 * @param $envelope
	 * @param $queue_obj
	 */
	public function do_sms_sqs_handler($envelope, $queue_obj)
	{
		try
		{
			echo $this->message(sprintf('-------- Process %s Task Start --------', $GLOBALS['AsyncTaskConfig']['TaskName']));
			$msg_body = $envelope->getBody();
			if (!empty($msg_body)) {
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_sms($msg_body);
				if ($task_flag) {
					echo $this->message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo $this->message(sprintf('process %s task [%s] ok', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);
				}
			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}
		$queue_obj->ack($envelope->getDeliveryTag());
	}

	public function do_wallets_log_handler($envelope, $queue_obj)
	{
		try {
			$msg_body = $envelope->getBody();
			if (!empty($msg_body)) {
				$msg_type = $envelope->getType();
				//$mt = $envelope->getTimeStamp();
				//echo sprintf("消息时间戳:%s[%s]\n", $mt, date('Y-m-d H:i:s', $mt));

				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_wallets_log($msg_body);
				if ($task_flag) {
					echo $this->message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo $this->message(sprintf('process %s task [%s] ok', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);
				}
			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}
		$queue_obj->ack($envelope->getDeliveryTag());
	}

	public function do_ccallback_sqs_handler($envelope, $queue_obj)
	{
		//$a = $GLOBALS['AsyncProcessObj']->getRemitOrder(2);
		//print_r($a);

		// 消息重新打回队列
		//$r = $queue_obj->nack($envelope->getDeliveryTag(), AMQP_REQUEUE);

		$msg_body = $envelope->getBody();
		try {

			//$msg_expiration = $envelope->getExpiration();
			//echo PHP_EOL."expir:".$msg_expiration.PHP_EOL;

			//$msg_time_stamp = $envelope->getTimeStamp();
			//$msg_type = $envelope->getType();

			// 消息的超时时间 这里可以看做延时时间
			//$msg_expiration = $envelope->getExpiration();

			echo $this->message(sprintf('---------- Process %s Task Start ----------', $GLOBALS['AsyncTaskConfig']['TaskName']));
			echo $this->message(sprintf('消息添加时间: %s 类型: %s', date('Y-m-d H:i:s', $envelope->getTimeStamp()), $envelope->getType()));
			$msg_headers = $envelope->getHeaders();
			if (isset($msg_headers['x-death'][0]['original-expiration'])){
				echo $this->message(sprintf('Delay Message Delayer Time: %s seconds', $msg_headers['x-death'][0]['original-expiration']/1000));
			}

			if (!empty($msg_body))
			{
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_chargeorder_callback($msg_body);
				if ($task_flag) {
					echo $this->message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo $this->message(sprintf('process %s task [%s] FAILED', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);

					// todo: 错误处理
				}

			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}

		//手动发送ACK应答
		$queue_obj->ack($envelope->getDeliveryTag());
	}

	public function do_wcallback_sqs_handler($envelope, $queue_obj)
	{

		$msg_body = $envelope->getBody();
		try {
			if (!empty($msg_body))
			{
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_withdraw_callback($msg_body);
				if ($task_flag) {
					echo $this->message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo $this->message(sprintf('process %s task [%s] ok', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);

					// todo: 错误处理
				}

			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}

		//手动发送ACK应答
		$queue_obj->ack($envelope->getDeliveryTag());
		// 打回消息
		//$queue_obj->nack($envelope->getDeliveryTag(), AMQP_REQUEUE);
	}

	public function do_check_corder_sqs_handler($envelope, $queue_obj)
	{
		try
		{
			$msg_body = $envelope->getBody();
			if (!empty($msg_body))
			{

				//$msg_type  = $envelope->getType();
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_check_chargeorder($msg_body);
				if ($task_flag) {
					echo self::message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo self::message(sprintf('process %s task [%s] ok', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);
				}
			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}
		$queue_obj->ack($envelope->getDeliveryTag());

	}

	public function do_check_worder_sqs_handler($envelope, $queue_obj)
	{
		try {
			$msg_body = $envelope->getBody();
			if (!empty($msg_body)) {
				$msg_type  = $envelope->getType();
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_check_withdraworder($msg_body);
				if ($task_flag) {
					echo self::message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {
					echo self::message(sprintf('process %s task [%s] ok', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);
				}
			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}
		$queue_obj->ack($envelope->getDeliveryTag());
	}

	public function do_scheduled_tasks_sqs_handler($envelope, $queue_obj)
	{
		try {
			echo $this->message(sprintf('-------- Process %s Task Start --------', $GLOBALS['AsyncTaskConfig']['TaskName']));
			$msg_body = $envelope->getBody();
			if (!empty($msg_body))
			{
				// 根据 msg_type 来区分任务类型
				$msg_type  = $envelope->getType();
				$RealProcess = new AsyncTaskProcess();
				$task_flag = $RealProcess->process_scheduled_tasks($msg_body, $msg_type);
				if ($task_flag) {
					echo $this->message(sprintf('Process %s Task OK', $GLOBALS['AsyncTaskConfig']['TaskName']));
				}
				else {

					echo $this->message(sprintf('process %s task [%s] failed', $GLOBALS['AsyncTaskConfig']['TaskName'], $msg_body), 3);
				}
			}
			else {
				echo $this->message('message body is empty', 2);
			}
		}
		catch (Exception $e) {
			$errMsg = sprintf('line %s in %s : %s', $e->getLine(), $e->getFile(), $e->getMessage());
			echo $this->message($errMsg, 3).PHP_EOL;
		}
		$queue_obj->ack($envelope->getDeliveryTag());
	}
}



