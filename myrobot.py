#!/usr/bin/python

import sys
import subprocess

filepath=sys.argv[1]


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_value(value):
	with open(filepath) as fp:  
   		line = fp.readline()
   		while line:
			line = fp.readline()
			if value in line:
				 return line.strip().split(" ")	[-1].strip()
				 
def get_version_num():
	return int(get_global("innodb_version").replace(".", ""))
				 
def get_single_value(value):
	with open(filepath) as fp:  
   		line = fp.readline()
   		while line:
			line = fp.readline()
			if value in line:
				line = fp.readline()
				line = fp.readline()
				return line.strip("|").split("|")[0].split()[0]
				
def get_global(statusVar, split=True):
	with open(filepath) as fp:  
   		line = fp.readline()
   		while line:
			line = fp.readline()
			if statusVar in line:
				 #disambiguate variables with same initial name
				if statusVar==line.strip("|").split("|")[0].strip():
					return line.strip("|").split("|")[1].split()[0] if split else line.strip("|").split("|")[1].strip()
		return None
		
def print_banner():
	print
	print bcolors.OKBLUE + "-- MYSQL ROBOT 0.1 by: mortensi --" + bcolors.ENDC
	
	
def check_mysql_version():
	print(get_global("version") + " " + get_global("version_comment", False) + " " + get_global("version_compile_machine"))
	print
	
	
def post_uptime_warning():
	print bcolors.OKBLUE + "ACTIVITY" + bcolors.ENDC
	uptime=int(get_global("uptime"))
	questions = int(get_global("questions"))
	d, s = divmod(uptime, 86400)
	h, r = divmod(s, 3600)
	m, rr = divmod(r, 3600)
	if uptime>172800:
		print "Uptime: " + "%d days %02d hours %02d minutes" % (d, h, m)
	else:
		print bcolors.FAIL + "Uptime: " + "%d days %02d hours %02d minutes" % (d, h, m) + bcolors.ENDC
	print "Questions: " + str(questions)
	print "Threads Connected: " + get_global("threads_connected")
	print "Avg. questions per second " + str(questions/uptime)
	
	
def check_slow_queries():
	print
	print bcolors.OKBLUE + "SLOW QUERIES" + bcolors.ENDC
	slowQueries=get_global("slow_queries")
	if int(slowQueries)!=0:
		print bcolors.WARNING + "Slow queries: " + slowQueries + " out of " + get_global("questions") + " questions" + bcolors.ENDC
	else:
		print "There are no slow queries!"
	if get_global("slow_query_log")=="ON":
		print "Slow query log enabled"
		print "Long query time is: " + get_global("long_query_time")
	else:
		print bcolors.WARNING + "Slow query log not enabled" + bcolors.ENDC
	
	
def check_binary_log():
	print
	print bcolors.OKBLUE + "BINARY UPDATE LOG" + bcolors.ENDC
	if get_global("log_bin")=="ON":
		print "The binary update log is enabled"
		if int(get_global("expire_logs_days"))==0:
			print bcolors.WARNING + "The expire_logs_days is not set." 
			print "The mysqld will retain the entire binary log until " 
        	print "RESET MASTER or PURGE MASTER LOGS commands are run manually" 
        	print "Setting expire_logs_days will allow you to remove old binary logs automatically" + bcolors.ENDC
		if int(get_global("sync_binlog"))==0:
			print bcolors.FAIL + "Binlog sync is not enabled, you could lose binlog records during a server crash" + bcolors.ENDC
		if int(get_global("sync_binlog"))>1:
			print bcolors.FAIL + "sync_binlog is > 1. Transactions are committed without having been synchronized to disk. Therefore, in the event of a power failure or operating system crash, it is possible that the server has committed some transactions that have not been synchronized to the binary log" + bcolors.ENDC
	else:
		print bcolors.FAIL + "The binary log is NOT enabled."
		print "You will not be able to do point in time recovery for backups taken from this instance" + bcolors.ENDC
	if get_global("log_slave_updates")=="ON":
		print "log_slave_updates is enabled"
		
		
def check_replication_config():
	print
	print bcolors.OKBLUE + "REPLICATION CONFIG" + bcolors.ENDC
	
	if get_global("log_bin")=="ON":
		binlog_cache_size=get_global("binlog_cache_size")
		binlog_stmt_cache_size=get_global("binlog_stmt_cache_size")
		binlog_cache_use=get_global("binlog_cache_use")
		binlog_stmt_cache_use=get_global("binlog_stmt_cache_use")
		binlog_cache_disk_use=int(get_global("binlog_cache_disk_use"))
		binlog_stmt_cache_disk_use=int(get_global("binlog_stmt_cache_disk_use"))
		print "binlog_cache_size is " + binlog_cache_size
		print "binlog_stmt_cache_size is " + binlog_stmt_cache_size
		print "Binlog_cache_use is " + binlog_cache_use
		print "Binlog_stmt_cache_use is " + binlog_stmt_cache_use
		if binlog_cache_disk_use!=0:
			print bcolors.FAIL + "Binlog_cache_disk_use is not zero: " + str(binlog_cache_disk_use) + bcolors.ENDC
		else:
			print bcolors.OKGREEN + "Binlog_cache_disk_use is zero" + bcolors.ENDC
		if binlog_stmt_cache_disk_use!=0:
			print bcolors.FAIL + "Binlog_stmt_cache_disk_use is not zero " + str(binlog_stmt_cache_disk_use) + bcolors.ENDC
		else:
			print bcolors.OKGREEN + "Binlog_stmt_cache_disk_use is zero" + bcolors.ENDC
	else:
		print "This instance is not binlogging"
		
		
def check_replication_slave():
	print
	print bcolors.OKBLUE + "REPLICATION SLAVE" + bcolors.ENDC
	if get_global("slave_allow_batching")=="OFF":
		print bcolors.WARNING + "NDB Cluster slave_allow_batching is set to OFF. Is it ok?" 
		print "With slave_allow_batching on, the slave mysqld prepares multiple row changes in a batch, and executes them together, to amortize the cost of messaging round trips between SQL and data nodes, that's were the bottleneck may be."
		print "The default batch size is 32 KB. You can configure this with the ndb_batch_size"
		print "Consider also that the slave applies updates in an epoch in batches, ensuring that all batches in a particular epoch execute before applying any batch in the next epoch" + bcolors.ENDC
	print "binlog_format is " + get_global("binlog_format")
	print bcolors.FAIL + "primary key??" + bcolors.ENDC
	print bcolors.FAIL + "Seconds_Behind_Master" + bcolors.ENDC
	print bcolors.FAIL + "Master_Log_File" + bcolors.ENDC
	print bcolors.FAIL + "Read_Master_Log_Pos" + bcolors.ENDC
	print bcolors.FAIL + "Relay_Log_File" + bcolors.ENDC
	print bcolors.FAIL + "Relay_Log_Pos" + bcolors.ENDC
	print bcolors.FAIL + "Relay_Master_Log_File" + bcolors.ENDC
	print bcolors.FAIL + "Exec_Master_Log_Pos" + bcolors.ENDC
	print bcolors.FAIL + "Slave_IO_Running" + bcolors.ENDC
	print bcolors.FAIL + "Slave_SQL_Running" + bcolors.ENDC
	
	# Checking the number of pending log file fsyncs
	innodb_os_log_pending_fsyncs = int(get_global("innodb_os_log_pending_fsyncs"))
	if innodb_os_log_pending_fsyncs!=0:
		print bcolors.FAIL + "innodb_os_log_pending_fsyncs is " + str(innodb_os_log_pending_fsyncs) + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "innodb_os_log_pending_fsyncs is 0" + bcolors.ENDC
		
	# Checking the number of pending log file writes
	innodb_os_log_pending_writes = int(get_global("innodb_os_log_pending_writes"))
	if innodb_os_log_pending_writes!=0:
		print bcolors.FAIL + "innodb_os_log_pending_writes is " + str(innodb_os_log_pending_writes) + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "innodb_os_log_pending_writes is 0" + bcolors.ENDC
		
	# Checking InnoDB capacity
	print "slave_allow_batching is " + get_global("slave_allow_batching")			
			
	# Checking if commit-related I/O operations are rearranged and done in batches
	innodb_flush_log_at_trx_commit = get_global("innodb_flush_log_at_trx_commit")
	print "innodb_flush_log_at_trx_commit is: " + innodb_flush_log_at_trx_commit
	if int(innodb_flush_log_at_trx_commit)==1:
		print bcolors.WARNING + "When slave is lagging, you can simply check if SET GLOBAL innodb_flush_log_at_trx_commit=2; solves it" + bcolors.ENDC
		
	# Checking parallel workers
	slave_parallel_workers = get_global("slave_parallel_workers")
	print "slave_parallel_workers is: " + slave_parallel_workers
	if int(slave_parallel_workers)==0:
		print bcolors.WARNING +  "If your master make changes in multiple databases more or less equally, you could try to setup a multi threaded slave by increasing slave_parallel_workers" + bcolors.ENDC


def check_threads():
	print
	print bcolors.OKBLUE + "WORKER THREADS" + bcolors.ENDC
	
	uptime=int(get_global("uptime"))
	threads_cached=get_global("threads_cached")
	print "Current thread_cache_size: " + get_global("thread_cache_size")
	print "Current threads_cached: " + threads_cached
	print bcolors.FAIL + "Current threads per second: ??" + bcolors.ENDC
	
	historic_threads_per_sec = int(get_global("threads_created"))/uptime
	print "Historic threads_per_sec: " + str(historic_threads_per_sec)
	
	if historic_threads_per_sec>= 2 and int(threads_cached<=1):
		print bcolors.FAIL + "Threads created per/sec are overrunning threads cached" 
		print "You should raise thread_cache_size" + bcolors.ENDC
	#elif current_threads_per_sec>=2:
	#	print bcolors.FAIL + "Threads created per/sec are overrunning threads cached"
	#	print "You should raise thread_cache_size" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Your thread_cache_size is fine" + bcolors.ENDC
	
	print "innodb_thread_concurrency: " +  get_global("innodb_thread_concurrency")
	print "innodb_read_io_threads: " + get_global("innodb_read_io_threads")
	print "innodb_write_io_threads: " + get_global("innodb_write_io_threads")


def check_used_connections():
	print
	print bcolors.OKBLUE + "MAX CONNECTIONS" + bcolors.ENDC
	
	max_used_connections=int(get_global("max_used_connections"))
	threads_connected=int(get_global("threads_connected"))
	max_connections=int(get_global("max_connections"))
	aborted_clients=int(get_global("aborted_clients"))
	aborted_connects=int(get_global("aborted_connects"))
	connection_errors_max_connections=int(get_global("connection_errors_max_connections"))
	
	if aborted_clients>0:
		print bcolors.FAIL + "aborted_clients is > 0: " + str(aborted_clients) + bcolors.ENDC	
		
	if aborted_connects>0:
		print bcolors.FAIL + "aborted_connects is > 0: " + str(aborted_connects) + bcolors.ENDC		
		
	if connection_errors_max_connections>0:
		print bcolors.FAIL + "Connection_errors_max_connections is $connection_errors_max_connections Please fix your applications to close connections when not needed"
		print bcolors.FAIL + "And consider implementing some client-side thread pool solution if this is available"
		print bcolors.FAIL + "Lowering wait_timeout in my.cnf could be a good idea too. Applications should handle lost connections, ideally." + bcolors.ENDC	
	
	connections_ratio=max_used_connections/max_connections
	print "Current max_connections: " + str(max_connections)
	print "Current threads_connected: " + str(threads_connected)
	print "Historic max_used_connections: " + str(max_used_connections)
	print "The number of used connections is " + str(connections_ratio) + "% of the configured maximum"
	if connections_ratio>=85:
		print bcolors.FAIL + "You should raise max_connections" + bcolors.ENDC	
	elif connections_ratio<=10:
		print bcolors.WARNING + "You are using less than 10% of your configured max_connections."
		print "Lowering max_connections could help to avoid an over-allocation of memory"
		print "See \"MEMORY USAGE\" section to make sure you are not over-allocating" + bcolors.ENDC	
	else:
		print bcolors.OKGREEN + "Your max_connections variable seems to be fine." + bcolors.ENDC	
		
		
def check_innodb_status():
	print
	print bcolors.OKBLUE + "INNODB STATUS" + bcolors.ENDC
		
	innodb_buffer_pool_size=get_global("innodb_buffer_pool_size")
	innodb_additional_mem_pool_size=get_global("innodb_additional_mem_pool_size")
	innodb_fast_shutdown=get_global("innodb_fast_shutdown")
	innodb_flush_log_at_trx_commit=get_global("innodb_flush_log_at_trx_commit")
	innodb_locks_unsafe_for_binlog=get_global("innodb_locks_unsafe_for_binlog")
	innodb_log_buffer_size=get_global("innodb_log_buffer_size")
	innodb_log_file_size=get_global("innodb_log_file_size")
	innodb_log_files_in_group=get_global("innodb_log_files_in_group")
	innodb_safe_binlog=get_global("innodb_safe_binlog")
	innodb_thread_concurrency=get_global("innodb_thread_concurrency")
	innodb_stats_sample_pages=get_global("innodb_stats_sample_pages")
	innodb_stats_persistent_sample_pages=get_global("innodb_stats_persistent_sample_pages")
	innodb_file_per_table=get_global("innodb_file_per_table")
	innodb_buffer_pool_pages_free=get_global("innodb_buffer_pool_pages_free")
	innodb_buffer_pool_pages_total=get_global("innodb_buffer_pool_pages_total")
		
	# Buffer pool
	print "Current innodb_buffer_pool_size: " + sizeof_fmt(int(innodb_buffer_pool_size))
	print "Depending on how much space your innodb indexes take up it may be safe to increase this value to up to 2 / 3 of total system memory"  		
	percent_innodb_buffer_pool_free=int(innodb_buffer_pool_pages_free)*100/int(innodb_buffer_pool_pages_total)
	print "Current InnoDB buffer pool free (innodb_buffer_pool_pages_free*100/innodb_buffer_pool_pages_total)= " + str(percent_innodb_buffer_pool_free) + "%"

	# Logical reads from the buffer pool
	innodb_buffer_pool_reads=get_global("innodb_buffer_pool_reads")
	innodb_buffer_pool_read_requests=get_global("innodb_buffer_pool_read_requests")
	percent_innodb_buffer_pool_missed=int(innodb_buffer_pool_reads)*100/int(innodb_buffer_pool_read_requests)
	if percent_innodb_buffer_pool_missed>10:
		print bcolors.FAIL + "Reads that were not satisfied with buffer pool (Innodb_buffer_pool_reads*100/Innodb_buffer_pool_read_requests): " + str(percent_innodb_buffer_pool_missed) + "%" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Reads that were not satisfied with buffer pool (Innodb_buffer_pool_reads*100/Innodb_buffer_pool_read_requests): " + str(percent_innodb_buffer_pool_missed) + "%" + bcolors.ENDC

	# Check innodb_stats_sample_pages
	if innodb_stats_sample_pages is not None:
		print "innodb_stats_sample_pages is: " + innodb_stats_sample_pages
		if int(innodb_stats_sample_pages)==8:
			print bcolors.WARNING + "Statistics sampled pages (innodb_stats_sample_pages) has default value (8). Update this parameter if you experiment poor index choices for large tables and tables in joins."
			print "The optimizer might choose very different query plans based on different estimates of index selectivity." + bcolors.ENDC
	if innodb_stats_persistent_sample_pages is not None:
		print "innodb_stats_persistent_sample_pages is: " + innodb_stats_persistent_sample_pages
		if int(innodb_stats_persistent_sample_pages)==20:
			print bcolors.WARNING + "Statistics sampled pages (innodb_stats_persistent_sample_pages) has default value (20). Update this parameter if you experiment poor index choices for large tables and tables in joins."
			print "The optimizer might choose very different query plans based on different estimates of index selectivity." + bcolors.ENDC
			
	# Check InnoDB file per table 
	if innodb_file_per_table=="OFF":
		print bcolors.WARNING + "innodb_file_per_table is disabled, are you sure you want to keep it as such?" + bcolors.ENDC

	# Check Log File Size
	print "Current innodb_log_file_size: " + sizeof_fmt(int(innodb_log_file_size))
	print "Current innodb_log_files_in_group: " + innodb_log_files_in_group

	log_sequence_number = get_value("Log sequence number")
	last_checkpoint_at = get_value("Last checkpoint at")
	if log_sequence_number is not None:
		print "Log sequence number: " +  log_sequence_number
		print "Last checkpoint at: " + last_checkpoint_at
		space_used=int(log_sequence_number)-int(last_checkpoint_at)
		space_available=int(innodb_log_file_size)*int(innodb_log_files_in_group)
		print "REDO space used: " + str(space_used)
		print "REDO space available: " + str(space_available)
	
		percent_used_log_space=space_used*100/space_available
		if percent_used_log_space>75:
			print bcolors.FAIL + "Using too much log space, consider increasing it: " + str(percent_used_log_space) + "%" + bcolors.ENDC
		else:
			print bcolors.OKGREEN + "Log space usage seems normal: " + str(percent_used_log_space) + "%" + bcolors.ENDC	
	

def total_memory_used():
	print
	print bcolors.OKBLUE + "MEMORY USAGE" + bcolors.ENDC

	max_used_connections=int(get_global("max_used_connections"))
	read_buffer_size=int(get_global("read_buffer_size"))
	read_rnd_buffer_size=int(get_global("read_rnd_buffer_size"))
	sort_buffer_size=int(get_global("sort_buffer_size"))
	thread_stack=int(get_global("thread_stack"))
	max_connections=int(get_global("max_connections"))
	join_buffer_size=int(get_global("join_buffer_size"))
	tmp_table_size=int(get_global("tmp_table_size"))
	max_heap_table_size=int(get_global("max_heap_table_size"))
	net_buffer_length=int(get_global("net_buffer_length"))
	innodb_buffer_pool_size=int(get_global("innodb_buffer_pool_size"))
	innodb_log_buffer_size=int(get_global("innodb_log_buffer_size"))
	key_buffer_size=int(get_global("key_buffer_size"))
	query_cache_size=get_global("query_cache_size")
	log_bin=get_global("log_bin")

	if get_global("innodb_additional_mem_pool_size") is None:
		innodb_additional_mem_pool_size=0
		
	if get_global("query_cache_size") is None:
		query_cache_size=0

	if log_bin=="ON":
		binlog_cache_size=int(get_global("binlog_cache_size"))
	else:
		binlog_cache_size=0

	if max_heap_table_size<=tmp_table_size:
		effective_tmp_table_size=int(max_heap_table_size)
	else:
		effective_tmp_table_size=int(tmp_table_size)
		
	per_thread_buffers=(read_buffer_size + read_rnd_buffer_size + sort_buffer_size + thread_stack + join_buffer_size + binlog_cache_size + net_buffer_length) * max_connections
	per_thread_max_buffers=(read_buffer_size + read_rnd_buffer_size + sort_buffer_size + thread_stack + join_buffer_size + binlog_cache_size + net_buffer_length) * max_used_connections

	global_buffers=innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size + key_buffer_size + int(query_cache_size)
	max_memory=global_buffers + per_thread_max_buffers
	total_memory=global_buffers + per_thread_buffers

	print "Configured InnoDB Buffer Pool Size: " + sizeof_fmt(innodb_buffer_pool_size)
	print "Configured Max Per-thread Buffers (read_buffer_size + read_rnd_buffer_size + sort_buffer_size + thread_stack + join_buffer_size + binlog_cache_size + net_buffer_length) * max_connections): " + sizeof_fmt(per_thread_buffers)
	print "Configured Max Global Buffers (innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size + key_buffer_size + query_cache_size + net_buffer_length): " + sizeof_fmt(global_buffers)
	print "Max Memory Ever Allocated (global_buffers + per_thread_max_buffers): " + sizeof_fmt(max_memory)
	print "Configured Max Memory Limit (global_buffers + per_thread_buffers): " + sizeof_fmt(total_memory)
	print "Plus " + sizeof_fmt(effective_tmp_table_size) + " per temporary table created"
	
	
def check_key_buffer_size():
	print
	print bcolors.OKBLUE + "KEY BUFFER" + bcolors.ENDC
	
	key_read_requests=int(get_global("key_read_requests"))
	key_reads=int(get_global("key_reads"))
	key_blocks_used=int(get_global("key_blocks_used"))
	#key_blocks_used=int(get_global("myisam_indexes"))
	key_blocks_unused=int(get_global("key_blocks_unused"))
	key_cache_block_size=int(get_global("key_cache_block_size"))
	key_buffer_size=int(get_global("key_buffer_size"))
	
	if key_reads==0:
		print bcolors.FAIL + "No key reads?!"
		print "Seriously look into using some indexes" + bcolors.ENDC
		key_cache_miss_rate=0
		key_buffer_free=int(((float(key_blocks_unused) * float(key_cache_block_size)) / float(key_buffer_size)) * 100)
	else:
		key_cache_miss_rate=key_read_requests / key_reads
		key_buffer_free=int(((float(key_blocks_unused) * float(key_cache_block_size)) / float(key_buffer_size)) * 100)

	print bcolors.WARNING + "Current MyISAM index space is missing" + bcolors.ENDC
	print "Current key_buffer_size: " + sizeof_fmt(key_buffer_size)
	print "key_cache_miss_rate is key_read_requests / key_reads: " + str(key_read_requests) + " / " + str(key_reads)
	print "Key cache miss rate is 1 : " + str(key_cache_miss_rate)
	print "Key buffer free ratio (key_blocks_unused * key_cache_block_size / key_buffer_size * 100): " + str(key_buffer_free) + "%"
	print "Key buffer free ratio: " + str(key_buffer_free) + "%"

	if key_cache_miss_rate <= 100 and key_cache_miss_rate > 0 and key_buffer_free <= 20:
		print bcolors.FAIL + "You could increase key_buffer_size" 
		print "It is safe to raise this up to 1/4 of total system memory;"
		print "assuming this is a dedicated database server." + bcolors.ENDC
	elif key_buffer_free <= 20 and key_buffer_size <= myisam_indexes:
		print bcolors.FAIL + "You could increase key_buffer_size" 
		print "It is safe to raise this up to 1/4 of total system memory;"
		print "assuming this is a dedicated database server." + bcolors.ENDC
	elif key_cache_miss_rate >= 10000 or key_buffer_free <= 50:
		print bcolors.FAIL + "Your key_buffer_size seems to be too high." 
		print "Perhaps you can use these resources elsewhere" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Your key_buffer_size seems to be fine" + bcolors.ENDC
		
		
def check_query_cache():
	print
	print bcolors.OKBLUE + "QUERY CACHE" + bcolors.ENDC
	
	mysql_version_num=get_version_num()
	if mysql_version_num>int("08000"):
		print bcolors.OKGREEN + "Query cache has been obsoleted on MySQL Server 8.x" + bcolors.ENDC
		return
	
	qcache_free_memory=int(get_global("qcache_free_memory"))
	qcache_total_blocks=int(get_global("qcache_total_blocks"))
	qcache_free_blocks=int(get_global("qcache_free_blocks"))
	qcache_lowmem_prunes=int(get_global("qcache_lowmem_prunes"))
	mysql_version=get_global("mysql_version")
	query_cache_size=int(get_global("query_cache_size"))
	query_cache_type=get_global("query_cache_type")
	query_cache_limit=int(get_global("query_cache_limit"))
	query_cache_min_res_unit=int(get_global("query_cache_min_res_unit"))
	
	if query_cache_type=="OFF":
		print bcolors.WARNING + "Query cache is not enabled"
		print "Perhaps you should set the query_cache_type" + bcolors.ENDC
		if query_cache_size!=0:
			print bcolors.WARNING + "Query cache is not enabled but query_cache_size is set, why waste $query_cache_size memory on it?" + bcolors.ENDC

		return
		
	if query_cache_size==0:
		print bcolors.FAIL + "Query cache is supported but not enabled"
		print "Perhaps you should set the query_cache_size" + bcolors.ENDC
	else:
		qcache_used_memory=query_cache_size-qcache_free_memory
		qcache_mem_fill_ratio=float(qcache_used_memory) * 100 / float(query_cache_size)
		print bcolors.OKGREEN + "Query cache is enabled" + bcolors.ENDC
		print "Current query_cache_size: " + sizeof_fmt(query_cache_size)
        print "Current query_cache_used: " + sizeof_fmt(qcache_used_memory)
        print "Current query_cache_limit: " + sizeof_fmt(query_cache_limit)
        print "Current Query cache Memory fill ratio: " + str(qcache_mem_fill_ratio) + "%"
        print "Current query_cache_min_res_unit: " + str(query_cache_min_res_unit)
        
        if qcache_free_blocks>2 and qcache_total_blocks>0:
        	qcache_percent_fragmented=float(qcache_free_blocks) * 100 / float(qcache_total_blocks)
        	if qcache_percent_fragmented>20:
        		print bcolors.FAIL + "Query Cache is $qcache_percent_fragmentedHR % fragmented"
        		print "Run \"FLUSH QUERY CACHE\" periodically to defragment the query cache memory"
        		print "If you have many small queries lower 'query_cache_min_res_unit' to reduce fragmentation." + bcolors.ENDC
        		
        if qcache_mem_fill_ratio<=25:
        	print bcolors.FAIL + "Your query_cache_size seems to be too high."
        	print bcolors.FAIL + "Perhaps you can use these resources elsewhere" + bcolors.ENDC
        	
        if qcache_lowmem_prunes>= 50 and qcache_mem_fill_ratio>=80:
        	print bcolors.FAIL + "However, " + qcache_lowmem_prunes + "queries have been removed from the query cache due to lack of memory"
        	print "Perhaps you should raise query_cache_size" + bcolors.ENDC
        	
        print bcolors.WARNING + "MySQL won't cache query results that are larger than query_cache_limit in size" + bcolors.ENDC

	
def check_sort_operations():
	print
	print bcolors.OKBLUE + "SORT OPERATIONS" + bcolors.ENDC
	
	sort_merge_passes=int(get_global("sort_merge_passes"))
	sort_scan=int(get_global("sort_scan"))
	sort_range=int(get_global("sort_range"))
	sort_buffer_size=int(get_global("sort_buffer_size"))
	read_rnd_buffer_size=int(get_global("read_rnd_buffer_size"))

	total_sorts=sort_scan + sort_range
	
	sort_buffer_size=sort_buffer_size + 8
	read_rnd_buffer_size=read_rnd_buffer_size + 8

	print "sort_buffer_size: " + sizeof_fmt(sort_buffer_size)
	print "Current sort_buffer_size: " + sizeof_fmt(sort_buffer_size)
	print "Current read_rnd_buffer_size: " + sizeof_fmt(read_rnd_buffer_size)

	if total_sorts == 0:
		print "No sort operations have been performed"
		passes_per_sort=0
	elif sort_merge_passes != 0:
		passes_per_sort=float(sort_merge_passes) / float(total_sorts)
	else:
		passes_per_sort=0

	if passes_per_sort >= 2:
		print bcolors.FAIL + "On average " + str(passes_per_sort) + " sort merge passes are made per sort operation"
		print "You should raise your sort_buffer_size "
		print "You should also raise your read_rnd_buffer_size" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Sort buffer seems to be fine, sort_merge_passes/total_sorts is: " + str(int(passes_per_sort)) + bcolors.ENDC


def check_join_operations():
	print
	print bcolors.OKBLUE + "JOINS" + bcolors.ENDC
	
	select_full_join=int(get_global("select_full_join"))
	select_range_check=int(get_global("select_range_check"))
	join_buffer_size=int(get_global("join_buffer_size"))

	## Some 4K is dropped from join_buffer_size adding it back to make sane ##
	## handling of human-readable conversion ##
	join_buffer_size=join_buffer_size + 4096

	print "Current join_buffer_size: " + sizeof_fmt(join_buffer_size)

	if select_range_check==0 and select_full_join==0:
		print bcolors.OKGREEN + "Your joins seem to be using indexes properly" + bcolors.ENDC
		
	if select_full_join>0:
		print bcolors.FAIL + "You have had " + str(select_full_join) + " queries where a join could not use an index properly" + bcolors.ENDC
		print_error=True
		raise_buffer=True
		
	if select_range_check>0:
		print bcolors.FAIL + "You have had $select_range_check joins without keys that check for key usage after each row" + bcolors.ENDC
		print_error=True
		raise_buffer=True

	if join_buffer_size>=4194304:
		print bcolors.FAIL + "join_buffer_size >= 4M (" + sizeof_fmt(join_buffer_size) + ")" 
		print "This is not advised" + bcolors.ENDC
		
	if print_error:
		print bcolors.FAIL + "You should enable \"log-queries-not-using-indexes\""
		print "Then look for non indexed joins in the slow query log." + bcolors.ENDC
		if raise_buffer:
			print bcolors.FAIL + "If you are unable to optimize your queries you may want to increase your"
			print "join_buffer_size to accommodate larger joins in one pass."
			print "Note! This script will still suggest raising the join_buffer_size when"
			print "ANY joins not using indexes are found." + bcolors.ENDC


def check_open_files():
	print
	print bcolors.OKBLUE + "OPEN FILES LIMIT" + bcolors.ENDC

	open_files=int(get_global("open_files"))
	open_files_limit=int(get_global("open_files_limit"))

	if open_files_limit==0:
		print bcolors.WARNING + "Current open_files_limit is zero" 
		print "You should check what value is set for ulimit -u" + bcolors.ENDC
	else:
		print "Current open_files_limit: " + str(open_files_limit)
		open_files_ratio= float(open_files) * 100 / float(open_files_limit)
		print "open_files/open_files_limit is: " + str(open_files_ratio)+ "%"

		print bcolors.WARNING + "The open_files_limit should typically be set to at least 2x-3x"
		print "that of table_open_cache if you have heavy MyISAM usage." + bcolors.ENDC
        
		if open_files_ratio>=75:
			print bcbcolors.FAIL + "You currently have open more than 75% of your open_files_limit" + bcolors.ENDC
		else:
			print bcolors.OKGREEN + "Your open_files_limit value seems to be fine" + bcolors.ENDC


def check_table_cache():
	print
	print bcolors.OKBLUE + "TABLE CACHE" + bcolors.ENDC

	open_tables=int(get_global("open_tables"))
	opened_tables=int(get_global("opened_tables"))
	open_table_definitions=int(get_global("open_table_definitions"))
	table_open_cache=int(get_global("table_open_cache"))
	table_definition_cache=int(get_global("table_definition_cache"))
	innodb_open_files=int(get_global("innodb_open_files"))
	innodb_file_per_table=get_global("innodb_file_per_table")
	table_open_cache_instances=int(get_global("table_open_cache_instances"))
	table_count=int(get_single_value("Total Number of Tables"))


	if table_open_cache_instances<16:
		print bcolors.FAIL + "table_open_cache_instances is " + str(table_open_cache_instances) + " and a value of 16 is recommended" + bcolors.ENDC

	if opened_tables!=0 and table_open_cache!=0:
		table_cache_hit_rate= float(open_tables) * 100 / float(opened_tables)
		table_cache_fill= float(open_tables) * 100 / float(table_open_cache)
	elif opened_tables==0 and table_open_cache!=0:
		table_cache_hit_rate=100
		table_cache_fill= float(open_tables) * 100 / float(table_open_cache)
	else:
		print bcolors.FAIL + "ERROR no table_open_cache?!" + bcolors.END

	print "Current table_open_cache: " + str(table_open_cache) + " tables"
	print "Open_tables: " + str(open_tables) + " tables"
	print "Opened_tables: " + str(opened_tables) + " tables"
	print "Current table_definition_cache: " + str(table_definition_cache) + " tables"
	print "Current innodb_open_files: " + str(innodb_open_files)
	print "Current innodb_file_per_table: " + innodb_file_per_table
	print bcolors.WARNING + "If both table_definition_cache and innodb_open_files are set, the highest setting is used." 
	print "innodb_open_files is only relevant if you use multiple InnoDB tablespaces. It specifies the maximum number of .ibd files that MySQL can keep open at one time." + bcolors.ENDC
		
	print "You have a total of: " + str(table_count) + " tables"
        
	if table_cache_fill < 95:
		print bcolors.OKGREEN + "You have " + str(open_tables) + " open tables. The table_open_cache value seems to be fine" + bcolors.ENDC
	elif table_cache_hit_rate<=85 or table_cache_fill>=95:
		print bcolors.FAIL + "You have " + str(open_tables) + " open tables."
		print "Current table_open_cache hit rate is: " + str(table_cache_hit_rate) + "%, while " + str(table_cache_fill) + " of your table cache is in use"
		print "You should probably increase your table_open_cache" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Current table_open_cache hit rate is " + table_cache_hit_rate + "%, while " + table_cache_fill + "% of your table cache is in use"
		print "The table cache value seems to be fine" + bcolors.ENDC

	if table_definition_cache<=table_count and table_count >= 100:
		print bcolors.FAIL +  "You should probably increase your table_definition_cache value." + bcolors.ENDC

        
def check_tmp_tables():
	print
	print bcolors.OKBLUE + "TEMP TABLES" + bcolors.ENDC
	
	created_tmp_tables=int(get_global("created_tmp_tables"))
	created_tmp_disk_tables=int(get_global("created_tmp_disk_tables"))
	tmp_table_size=int(get_global("tmp_table_size"))
	max_heap_table_size=int(get_global("max_heap_table_size"))
	internal_tmp_disk_storage_engine=get_global("internal_tmp_disk_storage_engine")
	
	mysql_version_num=get_version_num()

	if mysql_version_num>int("080002"):
		internal_tmp_mem_storage_engine=get_global("internal_tmp_mem_storage_engine")
		temptable_max_ram=get_global(temptable_max_ram)
		print "Using a MySQL 8 with:" 
		print "Temp internal tables engine: " + internal_tmp_mem_storage_engine
		print "Temp internal tables memory: " + temptable_max_ram

	print "Current max_heap_table_size: " + str(max_heap_table_size)
	print "Temp tables on disk engine: " + str(internal_tmp_disk_storage_engine)
	print "Current tmp_table_size: " + str(tmp_table_size)

	if tmp_table_size>max_heap_table_size:
		print bcolors.WARNING + "Effective in-memory tmp_table_size is limited to max_heap_table_size." + bcolors.ENDC

	if created_tmp_tables==0:
		tmp_disk_tables=0
	else:
		tmp_disk_tables=float(created_tmp_disk_tables) * 100 / (created_tmp_tables + created_tmp_disk_tables)

	print "Of " + str(created_tmp_tables) + " temp tables, " + str(round(tmp_disk_tables,2)) + "% were created on disk"

	if tmp_disk_tables>=25:
		print bcolors.FAIL + "Perhaps you should increase your temptable_max_ram, tmp_table_size and/or max_heap_table_size"
		print "to reduce the number of disk-based temporary tables" + bcolors.ENDC
		print bcolors.WARNING + "Note! BLOB and TEXT columns are not allow in memory tables." 
		print "If you are using these columns raising these values might not impact your "
		print "ratio of on disk temp tables." + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Created disk tmp tables ratio seems fine" + bcolors.ENDC


def check_table_scans():
	print
	print bcolors.OKBLUE + "TABLE SCANS" + bcolors.ENDC

	dml_reads=int(get_global("dml_reads"))
	read_rnd_next=int(get_global("handler_read_rnd_next"))
	read_buffer_size=int(get_global("read_buffer_size"))
	select_scan=int(get_global("select_scan"))

	print "Current read_buffer_size: " + sizeof_fmt(read_buffer_size)

	if dml_reads>0:
		full_table_scans=float(read_rnd_next) / float(dml_reads)
		print "Current table scan ratio (read_rnd_next/dml_reads)= " + str(round(full_table_scans,2)) + " : 1"
		if full_table_scans>=4000 and read_buffer_size<=2097152:
			print bcolors.FAIL + "You have a high ratio of sequential access requests to SELECTs"
			print "You may benefit from raising read_buffer_size and/or improving your use of indexes." + bcolors.ENDC
		elif read_buffer_size>8388608:
			print bcolors.FAIL + "read_buffer_size is over 8 MB "
			print "there is probably no need for such a large read_buffer" + bcolors.ENDC
		else:
			print bcolors.OKGREEN + "read_buffer_size seems to be fine" + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "read_buffer_size seems to be fine" + bcolors.ENDC

	if select_scan>0:
		print bcolors.WARNING + "The number of joins that did a full scan of the first table is " + str(select_scan) + bcolors.ENDC


def check_table_locking():
	print
	print bcolors.OKBLUE + "TABLE LOCKING" + bcolors.ENDC
	
	table_locks_waited=int(get_global("table_locks_waited"))
	table_locks_immediate=int(get_global("table_locks_immediate"))
	concurrent_insert=get_global("concurrent_insert")
	low_priority_updates=get_global("low_priority_updates")

	print "Table_locks_waited: " + str(table_locks_waited)
	print "Table_locks_immediate: " + str(table_locks_immediate)
	
	if table_locks_waited>0:
		immediate_locks_miss_rate=float(table_locks_immediate) / float(table_locks_waited)
		print bcolors.FAIL + "Current Lock Wait ratio (table_locks_immediate/table_locks_waited)= " + str(immediate_locks_miss_rate) + bcolors.ENDC

		if immediate_locks_miss_rate<5000:
			print bcolors.FAIL + "You may benefit from selective use of InnoDB." + bcolors.ENDC
			if low_priority_updates=="OFF":
				print bcolors.WARNING + "If you have long running SELECT's against MyISAM tables and perform"
 				print "frequent updates consider setting 'low_priority_updates=1'" + bcolors.ENDC
 			if concurrent_insert== "AUTO" or concurrent_insert=="NEVER":
				print bcolors.WARNING + "If you have a high concurrency of inserts on Dynamic row-length tables"
   				print "consider setting 'concurrent_insert=ALWAYS'." + bcolors.ENDC
	else:
		print bcolors.OKGREEN + "Your table locking seems to be fine" + bcolors.ENDC

	
	

print_banner()
#check_mysql_version()
post_uptime_warning()
check_slow_queries()
check_binary_log()
check_replication_config()
check_replication_slave()
check_threads()
check_used_connections()
check_innodb_status()
total_memory_used()
check_key_buffer_size()
check_query_cache()
check_sort_operations()
check_join_operations()
check_open_files()
check_table_cache()
check_tmp_tables()
check_table_scans()
check_table_locking()
