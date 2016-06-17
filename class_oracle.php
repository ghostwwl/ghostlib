<?php
/**
 * Created by PhpStorm.
 * User: ghostwwl
 */


class ClassOracle
{
    public $o_dbhost = null;
    public $o_dbport = '1521';
    public $o_dbuser = null;
    public $o_dbpwd = null;
    public $o_sid = null;
    public $o_conn_charset = 'AL32UTF8';
    public $link_id = false;
    public $connect_flag = false;
    public $debug_flag = true;

    public function __construct($o_dbh, $o_dbp, $o_dbuser, $o_dbpwd, $o_sid, $o_conn_char='AL32UTF8')
    {
        try
        {
            if (empty($o_dbh)) throw new Exception('unknown oracle db host');
            if (empty($o_dbp)) throw new Exception('unknown oracle db port');
            if (empty($o_dbuser)) throw new Exception('unknown oracle db user');
            if (empty($o_dbpwd)) throw new Exception('unknown oracle db password');
            if (empty($o_sid)) throw new Exception('unknown oracle db sid');

            $this->o_dbhost = $o_dbh;
            $this->o_dbport = $o_dbp;
            $this->o_dbuser = $o_dbuser;
            $this->o_dbpwd = $o_dbpwd;
            $this->o_sid = $o_sid;
            if (!empty($o_conn_char)) $this->o_conn_charset = $o_conn_char;
        }
        catch(Exception $err)
        {
            $err_msg = sprintf("ERROR %s] %s\n", date('Y-m-d H:i:s'), $err->getMessage());
            if ($this->debug_flag)
            {
                echo $err_msg;
            }
            else throw new Exception($err_msg);
        }
    }

    public function is_connect()
    {
        if ($this->link_id === false) return false;
        return true;
    }

    public function close()
    {
        oci_close($this->link_id);
    }


    public function connect()
    {
        try{
            $this->link_id = @oci_connect($this->o_dbuser, $this->o_dbpwd, "{$this->o_dbhost}:{$this->o_dbport}/{$this->o_sid}", $this->o_conn_charset);
            if (!$this->link_id){
                $e = oci_error();
                throw new Exception($e['message']);
            }
            return true;
        }
        catch(Exception $err){
            oci_close($this->link_id);
            $err_msg = sprintf("ERROR %s] %s\n", date('Y-m-d H:i:s'), $err->getMessage());
            if ($this->debug_flag) echo $err_msg;
            else throw new Exception($err_msg);
        }
        return false;
    }

    // 执行一条语句 执行完成后自动提交 query($sql, argv1, argv2, ...,argvn)
    // query('select * from xx where created>:pxc and deposit>:pxdep', ':pxc', 1381234563111, ':pxdep', 2000)
    public function &query()
    {
        $args_num = func_num_args();
        $args_list = func_get_args();
        if ($args_num < 1) throw new Exception('not found argument');
        if ($args_num % 2 !== 1) throw new Exception('invaild argument');
        $sql = $args_list[0];
        try
        {
            if (!$this->is_connect()) $this->connect();
            $stmt = @oci_parse($this->link_id, $sql);
            if (!$stmt){
                $e = oci_error($stmt);
                throw new Exception("oci_parse err:{$e['message']}");
            }
            // 绑定oracle 参数传入值
            if ($args_num > 1){
                for($i=1; $i<$args_num; $i=$i+2){
                    if (!isset($args_list[$i])) break;
                    $arg_p = $args_list[$i];
                    $arg_v = $args_list[$i+1];
                    oci_bind_by_name($stmt, $arg_p, $arg_v);
                }
            }

            $run_flag = oci_execute($stmt, OCI_COMMIT_ON_SUCCESS);
            if (!$run_flag){
                $e = oci_error($stmt);
                throw new Exception("<pre>execute err:{$e['message']}<br />\n".htmlentities($e['sqltext'])."</pre>");
            }
            $row_num = oci_fetch_all($stmt, $result, null, null, OCI_FETCHSTATEMENT_BY_ROW);
            @oci_free_statement($stmt);
            unset($stmt);
            return array('num'=>$row_num, 'result'=>$result);
        }
        catch(Exception $e){
            oci_close($this->link_id);
            $err_msg = sprintf("ERROR %s] %s\n", date('Y-m-d H:i:s'), $e->getMessage());
            if ($this->debug_flag) echo $err_msg;
            else throw new Exception($err_msg);
        }
        return null;
    }

    // 用于列表也翻页
    // select 要查询的语句 pageno 第几页  rows_per_page 每页取多少条
    public function &paged_result($select, $pageno, $rows_per_page)
    {
        try{
            if (!$this->is_connect()) $this->connect();
            $sql = "SELECT * FROM (SELECT r.*, ROWNUM as row_number FROM ({$select}) r WHERE ROWNUM<=:end_row) WHERE :start_row<=row_number";
            $stmt = oci_parse($this->link_id, $sql);
            if (!$stmt){
                $e = oci_error($stmt);
                throw new Exception("oci_parse err:{$e['message']}");
            }

            $start_row = ($pageno-1) * $rows_per_page + 1;

            oci_bind_by_name($stmt, ':start_row', $start_row);
            // Calculate the number of the last row in the page
            $end_row = $start_row + $rows_per_page - 1;
            oci_bind_by_name($stmt, ':end_row', $end_row);
            $run_flag = oci_execute($stmt);
            if (!$run_flag)
            {
                $e = oci_error($stmt);
                throw new Exception("<pre>execute err:{$e['message']}<br />\n".htmlentities($e['sqltext'])."</pre>");
            }
            // Prefetch the number of rows per page
            oci_set_prefetch($stmt, $rows_per_page);
            $row_num = oci_fetch_all($stmt, $result, null, null, OCI_FETCHSTATEMENT_BY_ROW);
            @oci_free_statement($stmt);
            unset($stmt);
            return $result;
        }
        catch(Exception $e)
        {
            oci_close($this->link_id);
            $err_msg = sprintf("ERROR %s] %s\n", date('Y-m-d H:i:s'), $e->getMessage());
            if ($this->debug_flag) echo $err_msg;
            else throw new Exception($err_msg);
        }
        return null;
    }


    // 执行update 或者insert 这个必须手动提交使用了事物
    // 如果单条insert 或者update 不使用事物 直接用 query
    public function execute($sqls)
    {
        if (!$this->is_connect()) $this->connect();
        foreach ($sqls as $sql)
        {
            $stmt = oci_parse($this->link_id, $sql);
            if (!oci_execute($stmt, OCI_DEFAULT))
            {
                oci_rollback($this->link_id);
                return false;
            }
        }
        return $this->commit();
    }

    public function commit()
    {
        try{
            $commit_flag = oci_commit($this->link_id);
            if (!$commit_flag) {
                $error = oci_error($this->link_id);
                throw new Exception('Commit failed. Oracle reports: ' . $error['message']);
            }
            return true;
        }
        catch(Exception $err){
            oci_close($this->link_id);
            $err_msg = sprintf("ERROR %s] %s\n", date('Y-m-d H:i:s'), $err->getMessage());
            if ($this->debug_flag) echo $err_msg;
            else throw new Exception($err_msg);
        }
        return false;
    }
}

?>
