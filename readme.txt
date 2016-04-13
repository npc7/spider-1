###############################################################################################################
                                     help document
###############################################################################################################
1.  start_urls: paras eg: {page}:0;{type}:0|1|2
    paras  must start with '{page}',other paras after it. 2 parameters in total.
2.  rules:the xpath must be in front of python code
    it allows multiple rule,every one can hava xpath and python expression,eg:
    xpath_expr;list#xpath_expr{py:}
3.  code comments : notice the smart jump of expression:'exp1 and exp2 or exp3'
    if exp1 is true,will return exp2 ,but if the value of exp2 is null string ,
    expression will return exp3
    eg:re.sub(r'\D','','%s')
4.  is_next :you can find the next page tag by multiple xpath,any one find a target
    tag ,crawler will go on.
    you can also add a python expression to help you to decide go on or break ,but notice,
    your python code must return TRUE(go on) or FALSE(break).
5.  what will we do for the new data item?
    almost,we will update the field cralwer.get_time with the now time, we can know what time
    we get the data. We also crawl the web site every day, and try to insert all the data item
    into our table,if it exists,we will update crawler.update_time.


FRQS:   1.when to encode and when to decode ?
        ans: set the default encoding before start doing something.

rules :
    field:  the item start with "_" will not be store in DataBase
            the item end with "_" shows it comes from parent .


###############################################################################################################
                                     create tabale sql scripts
###############################################################################################################

CREATE TABLE `feed` (
  `data_id` int(11) NOT NULL AUTO_INCREMENT,
  `spider_name` varchar(50) NOT NULL COMMENT '爬虫名称',
  `url` varchar(1000) NOT NULL COMMENT '起始链接地址',
  `paras` varchar(200) DEFAULT NULL COMMENT '除了page以外的其他参数:比如来源类型：商户或个人等',
  `py_url` varchar(255) DEFAULT NULL COMMENT '对url请求之前进行一些预处理',
  `py_html` varchar(255) DEFAULT NULL COMMENT '对获取到的html进行一些预处理',
  `table_from` varchar(50) DEFAULT NULL COMMENT '数据来源表',
  `table_save` varchar(50) NOT NULL COMMENT '数据存储表',
  `page_ttype` varchar(20) NOT NULL COMMENT '终端类型，手机端或者电脑端',
  `page_dtype` varchar(20) NOT NULL COMMENT '页面文档的格式，html，xml，或者json',
  `store` varchar(20) NOT NULL COMMENT '存储方式（insert|update和syn|his的组合，中间'':''链接）',
  `comments` varchar(100) DEFAULT NULL COMMENT '描述备注信息',
  PRIMARY KEY (`data_id`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8;


CREATE TABLE `rules` (
  `rule_id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(20) DEFAULT NULL COMMENT '爬虫名字，需要和start_urls表中spider_name对应',
  `db_field` varchar(20) DEFAULT NULL COMMENT '对应存储到数据库中的位置,格式"表明.字段名"(demo:car_info.data_id)',
  `path` varchar(200) DEFAULT NULL COMMENT '解析数据对应xpath表达式',
  `comments` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`rule_id`)
) ENGINE=InnoDB AUTO_INCREMENT=187 DEFAULT CHARSET=utf8;


CREATE TABLE `car_info` (
  `data_id` varchar(50) NOT NULL COMMENT '在对应网站上的唯一id\r\n',
  `ref_url` varchar(1000) DEFAULT NULL COMMENT '父链接',
  `url` varchar(1000) DEFAULT NULL COMMENT '数据来源页面链接地址',
  `is_crawl` int(11) unsigned zerofill DEFAULT '00000000000' COMMENT '采集标识',
  `crawl_times` int(11) unsigned zerofill DEFAULT '00000000000' COMMENT '采集次数统计',
  `get_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `pid` varchar(20) DEFAULT NULL COMMENT '进程标识号',
  `page` varchar(20) DEFAULT NULL COMMENT '分页页码',
  `info_ttype` varchar(20) DEFAULT NULL COMMENT '采集该页详细信息时的终端类型',
  `site` varchar(20) DEFAULT NULL COMMENT '站点名称,继承自start_url',
  `tag` varchar(20) DEFAULT NULL COMMENT '采集分类，继承自start_url',
  PRIMARY KEY (`data_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

