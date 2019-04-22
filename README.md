#### 新闻更新提醒
	
	实时监测目标平台的新闻更新，并将更新内容推送到指定邮箱

#### 环境及用法

##### 环境

* liunx
* crontab
* python3+
* BeautifulSoup4
* pymysql

##### 用法

* 脚本需要安装py3+，需要的库BeautifulSoup4，pymysql  
* clone脚本项目之后还需要在脚本目录新建一个.env配置文件，配置文件参数和格式见下方	
* crontab定时执行脚本

##### 配置文件.env
	
	{
		'sender':'',			//发送者邮箱
		'mail_pass':'',			//邮箱密码或密钥
		'mail_user':'',         //邮箱用户名
		'receivers':'',         //接收者
		'hosts':'127.0.0.1',
		'db_usr':'root',
		'db_pwd':'root',
		'db_name':'news'
	}

#### 目录

	|-- collection.py	新浪微博个人主页实时更新提醒	
	|-- .env            环境配置文件
	|-- README.md       说明文档

