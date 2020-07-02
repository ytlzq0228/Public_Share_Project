本文主要介绍，如何通过企业微信API向AD域账号即将过期的用户推送消息，以提醒用户尽快修改密码。
**主要涉及技术点：**

> 1、AD域控制器Dsquery命令
>  2、认识企业微信用户信息JSON数据结构 
>  3、Python JSON数据结构解释和取值
>  4、Python 字典数据结构赋值取值
> 4、企业微信消息推送API接口的使用

## 更好的阅读体验，可以移步CSDN博客
[【逗老师带你学IT】通过企业微信推送AD域密码即将到期提醒](https://blog.csdn.net/ytlzq0228/article/details/107073601)

# 一、获取密码即将过期的AD与账号
## 1、先决条件
首先，你需要部署一台AD域控制器。dsquery仅在DC和GC上运行有效，且可以是只读的DC或GC
## 2、关于DC和GC
### DC：域控制器(Domain Controller)
在Windows Server系统中，域控制器(domain controller , DC)是一个在Windows服务器域中的接受安全认证请求(登录, 检查权限, 等)的服务器。是一台装有活动目服务的计算机（我们经常说到的DC服务器）
### GC：全局编录（ Global Catalog）
包含森林中所有对象信息的特殊目录数据库

全局编录是存储林中所有 Active Directory 对象的副本的域控制器。全局编录存储林中主持域的目录中所有对象的完全副本，以及林中所有其他域中所有对象的部分副本

全局编录中包含的所有域对象的部分副本是用户搜索操作中最常使用的部分。作为其架构定义的一部分，这些属性被标记为包含到全局编录中。在全局编录中存储所有域对象的最常搜索的属性，可以为用户提供高效的搜索，而不会以不必要的域控制器参考影响网络性能。

在林中的初始域控制器上，会自动创建全局编录。可以向其他域控制器添加全局编录功能，或者将全局编录的默认位置更改到另一个域控制器上。

全局编录允许用户在林中的所有域中搜索目录信息，而不论数据存储在何处。执行林内的搜索时可获得最大的速度并使用最小的网络通信。

## 3、Dsquery命令

```shell
dsquery user -stalepwd 173 -o upn -limit 0
```
其中：
`dsquery user`表示查询用户
`-stalepwd 173`表示最后一次修改密码时间>173天，假使密码有效期180天，获取7天后即将过期的账号列表。
`-o upn`表示输出格式为upn
`-limit 0`指定传回符合搜寻条件的对象数目，如果值是 0，将传回所有符合的对象。如果不指定此参数，根据默认将只显示前 100 个结果。

dsquery命令是AD域控管理中常用的一个查询命令，更多详细信息可以参考：
[【逗老师带你学IT】AD域控 Dsquery 查询命令实例汇总](https://ctsdn.blog.csdn.net/article/details/107074237)
查询出的结果如下图所示，接下来我们要对这个信息进行处理，并转换成企业微信的UserID：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200701233340201.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
# 二、企业微信用户信息获取和查询
企业微信API文档原文写的很详细，清晰，易懂。本文会直接注明各接口在开发者文档中的位置，需要更多信息可以直接参考开发者文档，原文链接如下：
[企业微信开发文档【服务端API】](https://work.weixin.qq.com/api/doc/90000/90135/90664)
## 1、企业微信API认证token获取
#### 接口说明
**文档位置：**
**开发指南>获取access_token**
获取access_token是调用企业微信API接口的第一步，相当于创建了一个登录凭证，其它的业务API接口，都需要依赖于access_token来鉴权调用者身份。
 **接口定义：**
**请求方式：**  GET（HTTPS）
**请求地址：**  `https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ID&corpsecret=SECRET`
注：此处标注大写的单词ID和SECRET，为需要替换的变量，根据实际获取值更新。其它接口也采用相同的标注，不再说明。
#### 参数说明
参数|必须|说明
-|-|:-
corpid|是|企业ID，获取方式参考：[术语说明-corpid](https://work.weixin.qq.com/api/doc/90000/90135/90665#corpid)
corpsecret|是|应用的凭证密钥，获取方式参考：[术语说明-secret](https://work.weixin.qq.com/api/doc/90000/90135/90665#secret)
#### 返回结果示例

```python
{
   "errcode": 0,
   "errmsg": "ok",
   "access_token": "accesstoken000001",
   "expires_in": 7200
}
```
#### Python代码示例

```python
CORPID="ww078964********a08b1"
CORPSECRET="EHH***********************19Kw"

def gettoken():
	try:
		headers = {"Content-Type": "text/plain"}
		request = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CORPID+"&corpsecret="+CORPSECRET,headers=headers)
		request=json.loads(request.text)
		access_token=request['access_token']
		#提取JSON结构体中access_token字段值
	except Exception as err:
		raise err
	else:
		return access_token
```
#### Python数据结构-JSON取值
上面的Python示例中使用到了JSON数据结构的取值，Python自带一个很方便的JSON解释器，开局一句import json
之后

```python
json_data=json.loads(JSON数据原文)
value=json_data['取值的字段名']
```
即可得到想要的字段的值
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200702011249904.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

## 2、企业微信用户信息查询
### 2.1 读取指定成员信息
#### 接口说明
**文档位置：**
**通讯录管理>成员管理>读取成员**
在通讯录同步助手中此接口可以读取企业通讯录的所有成员信息，而自建应用可以读取该应用设置的可见范围内的成员信息。
**接口定义：**
**请求方式：** GET（HTTPS）
**请求地址：** `https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&userid=USERID`
#### 参数说明
参数|必须|说明
:-|-|:-
access_token|是|调用接口凭证
userid|是|成员UserID。对应管理端的帐号，企业内必须唯一。不区分大小写，长度为1~64个字节
### 2.2 批量读取部门成员信息，包括根部门（全员）
#### 接口说明
**文档位置：**
**通讯录管理>成员管理>获取部门成员详情**
**接口定义：**
**请求方式：** GET（HTTPS）
**请求地址：** `https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=ACCESS_TOKEN&department_id=DEPARTMENT_ID&fetch_child=FETCH_CHILD`
#### 参数说明
参数|必须|说明
:-|-|:-
access_token|是|调用接口凭证
department_id|是|获取的部门id，根部门ID为1
fetch_child|否|1/0：是否递归获取子部门下面的成员
### 2.3 企业微信用户信息JSON字段解释
#### 参数说明
参数|说明
-|:-
errcode|返回码
errmsg|对返回码的文本描述内容
userlist|成员列表
userid|成员UserID。对应管理端的帐号
name|成员名称，此字段从2019年12月30日起，对新创建第三方应用不再返回，2020年6月30日起，对所有历史第三方应用不再返回，后续第三方仅通讯录应用可获取，第三方页面需要通过通讯录展示组件来展示名字
mobile|手机号码，第三方仅通讯录应用可获取
department|成员所属部门id列表，仅返回该应用有查看权限的部门id
order|部门内的排序值，32位整数，默认为0。数量必须和department一致，数值越大排序越前面。
position|职务信息；第三方仅通讯录应用可获取
gender|性别。0表示未定义，1表示男性，2表示女性
email|邮箱，第三方仅通讯录应用可获取
is_leader_in_dept|表示在所在的部门内是否为上级；第三方仅通讯录应用可获取
avatar|头像url。第三方仅通讯录应用可获取
thumb_avatar|头像缩略图url。第三方仅通讯录应用可获取
telephone|座机。第三方仅通讯录应用可获取
alias|别名；第三方仅通讯录应用可获取
status|激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
extattr|扩展属性，第三方仅通讯录应用可获取
qr_code|员工个人二维码，扫描可添加为外部联系人；第三方仅通讯录应用可获取
external_profile|成员对外属性，字段详情见对外属性；第三方仅通讯录应用可获取
external_position|对外职务。 第三方仅通讯录应用可获取
address|地址，第三方仅通讯录应用可获取
hide_mobile|是否隐藏手机号
english_name|英文名
open_userid|全局唯一。对于同一个服务商，不同应用获取到企业内同一个成员的open_userid是相同的，最多64个字节。仅第三方应用可获取
main_department|主部门
#### 返回结果示例：
需要注意的是，之后我们通过推送信息API发送消息的时候，用户信息UserID字段与AD域控中的email或者CN Name字段大概率是不同的。在本例中，仅email字段可以做到完全一致。因此，我们的思路是，通过email查找企业微信用户的UserID，并使用该UserID向用户发送信息。

```python
{
    "errcode": 0,
    "errmsg": "ok",
    "userlist": [{
        "userid": "zhangsan",
        "name": "李四",
        "department": [1, 2],
        "order": [1, 2],
        "position": "后台工程师",
        "mobile": "13800000000",
        "gender": "1",
        "email": "zhangsan@gzdev.com",
        "is_leader_in_dept": [1, 0],
        "avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0",
        "thumb_avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/100",
        "telephone": "020-123456",
        "alias": "jackzhang",
        "status": 1,
        "address": "广州市海珠区新港中路",
        "hide_mobile" : 0,
        "english_name" : "jacky",
        "open_userid": "xxxxxx",
        "main_department": 1,
        "extattr": {
            "attrs": [
                {
                    "type": 0,
                    "name": "文本名称",
                    "text": {
                        "value": "文本"
                    }
                },
                {
                    "type": 1,
                    "name": "网页名称",
                    "web": {
                        "url": "http://www.test.com",
                        "title": "标题"
                    }
                }
            ]
        },
        "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode?vcode=xxx",
        "external_position": "产品经理",
        "external_profile": {
            "external_corp_name": "企业简称",
            "external_attr": [{
                    "type": 0,
                    "name": "文本名称",
                    "text": {
                        "value": "文本"
                    }
                },
                {
                    "type": 1,
                    "name": "网页名称",
                    "web": {
                        "url": "http://www.test.com",
                        "title": "标题"
                    }
                },
                {
                    "type": 2,
                    "name": "测试app",
                    "miniprogram": {
                        "appid": "wx8bd80126147dFAKE",
                        "pagepath": "/index",
                        "title": "miniprogram"
                    }
                }
            ]
        }
    }]
}
```
#### Python代码示例：

```python
def user_dict(access_token):
	try:
		user_dict=dict()
		headers = {"Content-Type": "text/plain"}
		request = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token="+access_token+"&department_id=1&fetch_child=1",headers=headers)
		request=json.loads(request.text)
		all_user_list=request['userlist']
		for user in all_user_list:
			#敲黑板，此处用到二级JSON取值
			userid=user['userid']
			username=user['name']
			email=user['email']
			email_fix=email.find("@")
			CNname=email[:email_fix]
			user_dict[CNname]=[userid,username,email]
	except Exception as err:
		raise err
	else:
		return user_dict
		#返回一个字典格式的结构体，字典内嵌一个list,结构示例如下:
		'CNname(邮箱前缀)': ['userid', 'username', 'email']
		'zhaoxy12149': ['ZhaoXiaoYun', '花和尚', 'zhaoxy12149@csdn.com']
```
#### Python数据结构-字典赋值（添加、修改记录）
上面的Python示例中使用到了字典的赋值，字典数据结构对于大量的记录可以快速进行查找，避免使用list等结构查找数据时需要频繁的for循环。
`user_dict=dict()`语句使用`dict()`创建一个空的字典
对于添加、修改已有记录，直接对字典的主键赋值即可。主键已经存在则会修改已有记录，主键不存在则会创建新的记录。

```python
user_dict[’AAA‘]='AAA_Value'
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200702012251107.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
注意，字典中记录的值，可以是字符串，也可以是list等其他数据结构。非常灵活。
### 2.4 通过AD域账户查询企业微信UserID
#### Python代码示例
```python
#输入CNname为邮箱前缀格式
def userid(user_dict,CNname):
	try:
		get_userid=get_username=get_email='N/A'
		get_userid=user_dict[CNname][0]
		get_username=user_dict[CNname][1]
		get_email=user_dict[CNname][2]
		#字典的value为一个list，分别获取list的0、1、2号元素
	except Exception as err:
		print("Get userid failed with CNname:"+CNname)
		raise err
	else:
		return get_userid,get_username,get_email
```

#### Python数据结构-字典取值
上面的Python示例中使用到了字典数据结构的取值
对于字典的数据结构，假使有如下字典:
person = {'name':'xiaoming', 'age':18}
最简单的一种方式：
`person['name']`即可得到name的value，值为“xiaoming”
另外一种方式：
`person.get('name')`也可以得到name的value。
两种方式的区别为，第一种如果键查不到抛异常，第二种查不到赋值为空，第二种方式也可以设置返回默认值。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200702010354772.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
# 三、企业微信应用消息推送
## 1、企业微信应用消息推送
### 1.1 调用应用消息推送接口
#### 接口说明
**文档位置：**
**消息推送>发送应用消息**
应用支持推送文本、图片、视频、文件、图文等类型。
**接口定义：**
**请求方式：** POST（HTTPS）
**请求地址：** `https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=ACCESS_TOKEN`
#### 参数说明
参数|必须|说明
:-|-|:-
access_token|是|调用接口凭证
### 1.2 发送请求内容
企业微信消息推送支持推送以下格式的消息：

> 文本消息
> 图片消息
> 语音消息
> 视频消息
> 文件消息
> 文本卡片消息
> 图文消息
> 图文消息（mpnews）
> markdown消息
> 小程序通知消息
> 任务卡片消息

#### 发送请求示例

```python
{
   "touser" : "UserID1|UserID2|UserID3",
   "toparty" : "PartyID1|PartyID2",
   "totag" : "TagID1 | TagID2",
   "msgtype" : "text",
   "agentid" : 1,
   "text" : {
       "content" : "你的快递已到，请携带工卡前往邮件中心领取。\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。"
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}
```
#### 参数说明
参数|必须|说明
:-|-|:-
touser|否|指定接收消息的成员，成员ID列表（多个接收者用‘\|’分隔，最多支持1000个）。特殊情况：指定为@all”，则向该企业应用的全部成员发送
toparty|否|指定接收消息的部门，部门ID列表，多个接收者用‘\|’分隔，最多支持100个。当touser为”@all”时忽略本参数
totag|否|指定接收消息的标签，标签ID列表，多个接收者用‘\|’分隔，最多支持100个。当touser为”@all”时忽略本参数
agentid|是|企业应用的id，整型。企业内部开发，可在应用的设置页面查看[查看方式](https://work.weixin.qq.com/api/doc/90000/90135/90665#agentid)；第三方服务商，可通过接口[获取企业授权信息](https://work.weixin.qq.com/api/doc/10975#%E8%8E%B7%E5%8F%96%E4%BC%81%E4%B8%9A%E6%8E%88%E6%9D%83%E4%BF%A1%E6%81%AF)获取该参数值.

> **`touser、toparty、totag`不能同时为空，后面不再强调。**

#### Python代码示例
以下为一个markdown格式的请求代码示例
```python
class post:
	def message(access_token,agentid,userid,username):
		try:
			headers = {"Content-Type": "text/plain"}
			data={
			"touser" : userid,
			"msgtype": "markdown",
			"agentid" : agentid,
			"markdown": {
					"content": '''**<font color="warning">【重要提示】</font>**
					>亲爱的**'''+username+'''**，您好：
					>
					>您的域账号密码即将过期，域账号密码有效期为180天
					>
					>请及时访问[**erp.csdn.com**](https://erp.csdn.com/Password.html)修改您的域账号密码。
					>
					>密码过期未修改会导致您无法连接集团WIFI，VPN，以及无法登陆各种业务系统！
					>
					>忘记域账号密码，请通过以下路径自助重置：
					>**ERP系统->新建申请->自助账号密码重置->AD域密码重置**'''
			},
			"enable_duplicate_check": 0,
			"duplicate_check_interval": 1800
			}
			request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token,headers=headers,json=data)
		except Exception as err:
			raise err
		else:
			return request.text
```
消息效果：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200702002801519.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
# 四、Python代码全文

```python
import json
import requests
import os

CORPID="ww0******08b1"
AGENTID="1*******2"
CORPSECRET="EHHs2FC********************DHDJ19Kw"

def read_file_as_str(file_path):
	# 判断路径文件存在
	if not os.path.isfile(file_path):
		raise TypeError(file_path + " does not exist")
	
	all_the_text = open(file_path).read()
	# print type(all_the_text)
	return all_the_text
	

def gettoken():
	try:
		headers = {"Content-Type": "text/plain"}
		request = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CORPID+"&corpsecret="+CORPSECRET,headers=headers)
		request=json.loads(request.text)
		access_token=request['access_token']
	except Exception as err:
		raise err
	else:
		return access_token

class weixin:
	class get:
		def userid(user_dict,CNname):
			try:
				get_userid=get_username=get_email='N/A'
				get_userid=user_dict[CNname][0]
				get_username=user_dict[CNname][1]
				get_email=user_dict[CNname][2]
			except Exception as err:
				print("Get userid failed with CNname:"+CNname)
				raise err
			else:
				return get_userid,get_username,get_email
			
		def userinfo_verbose(access_token,userid):
			try:
				headers = {"Content-Type": "text/plain"}
				request = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token="+access_token+"&userid="+userid,headers=headers)
			except Exception as err:
				raise err
			else:
				return request.text
				
		def user_dict(access_token):
			try:
				user_dict=dict()
				headers = {"Content-Type": "text/plain"}
				request = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token="+access_token+"&department_id=1&fetch_child=1",headers=headers)
				request=json.loads(request.text)
				all_user_list=request['userlist']
				for user in all_user_list:
					userid=user['userid']
					username=user['name']
					email=user['email']
					email_fix=email.find("@")
					CNname=email[:email_fix]
					user_dict[CNname]=[userid,username,email]
			except Exception as err:
				raise err
			else:
				return user_dict
				
			
	class post:
		def message(access_token,agentid,userid,username):
			try:
				headers = {"Content-Type": "text/plain"}
				data={
				"touser" : userid,
				"msgtype": "markdown",
				"agentid" : agentid,
				"markdown": {
						"content": '''**<font color="warning">【重要提示】</font>**
					>亲爱的**'''+username+'''**，您好：
					>
					>您的域账号密码即将过期，域账号密码有效期为180天
					>
					>请及时访问[**erp.csdn.com**](https://erp.csdn.com/Password.html)修改您的域账号密码。
					>
					>密码过期未修改会导致您无法连接集团WIFI，VPN，以及无法登陆各种业务系统！
					>
					>忘记域账号密码，请通过以下路径自助重置：
					>**ERP系统->新建申请->自助账号密码重置->AD域密码重置**'''
				},
				"enable_duplicate_check": 0,
				"duplicate_check_interval": 1800
				}
				request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token,headers=headers,json=data)
			except Exception as err:
				raise err
			else:
				return request.text

def main():
	try:
		command=os.popen("dsquery user -stalepwd 173 -o upn -limit 0")
		#使用OS功能调用Windows系统命令行
		user_list_file=command.read()
		#读取OS系统命令行的回显
		user_list_file=user_list_file.replace('""\n','').replace('"','').replace('@csdn.com','')
		sent_user_list=user_list_file.split("\n")
		#将原始数据格式化成list结构
		access_token=gettoken()
		#获取access_token
		user_dict=weixin.get.user_dict(access_token)
		#读取全员信息
		for i in range(len(sent_user_list)-1):
			try:
				userid,username,email=weixin.get.userid(user_dict,sent_user_list[i])
			except Exception as err:
				print(err)
			else:
				print(userid,username,email)
				sent_result=weixin.post.message(access_token,AGENTID,userid,username)
		
	except Exception as err:
		print(err)


if __name__ == '__main__':
	main()
```
往期回顾：
[【逗老师带你学IT】Google Admin服务账号+API管理G suit内所有网域用户](https://blog.csdn.net/ytlzq0228/article/details/105682567)
[【逗老师带你学IT】PRTG监控系统通过企业微信推送图文混排告警消息](https://blog.csdn.net/ytlzq0228/article/details/105525667)
[【逗老师带你学IT】PRTG HTTP API获取指定传感器流量图表图片](https://blog.csdn.net/ytlzq0228/article/details/105524615)
[【逗老师带你学IT】PRTG监控系统合并多个传感器通道数据](https://blog.csdn.net/ytlzq0228/article/details/104736297)
[【逗老师带你学IT】PRTG监控系统通过企业微信推送告警消息](https://blog.csdn.net/ytlzq0228/article/details/104733958)
[【逗老师带你学IT】PRTG监控系统配合树莓派采集企业内部无线网络质量](https://blog.csdn.net/ytlzq0228/article/details/104739756)
[【逗老师带你学IT】vMware ESXi 6.7合并第三方硬件驱动](https://blog.csdn.net/ytlzq0228/article/details/105194719)
[【逗老师带你学IT】Kiwi Syslog Server安装和配置教程](https://blog.csdn.net/ytlzq0228/article/details/104827014)
[【逗老师带你学IT】Kiwi Syslog Web Access与Active Directory集成认证](https://blog.csdn.net/ytlzq0228/article/details/104826989)
[【逗老师带你学IT】vMware ESXi 6.7合并第三方硬件驱动](https://blog.csdn.net/ytlzq0228/article/details/105194719)
[【逗老师带你学IT】Windows Server Network Policy Service（NPS）记账与审计](https://blog.csdn.net/ytlzq0228/article/details/104760054)
[【逗老师带你学IT】Windows Server NPS服务构建基于AD域控的radius认证](https://blog.csdn.net/ytlzq0228/article/details/104758242)
[【逗老师带你学IT】AD域控和freeradius集成认证环境，PAP，MSCHAPV2](https://blog.csdn.net/ytlzq0228/article/details/104757395)
[【逗老师带你学IT】深信服SSL远程接入与深信服行为审计同步登陆用户信息](https://blog.csdn.net/ytlzq0228/article/details/104723838)
