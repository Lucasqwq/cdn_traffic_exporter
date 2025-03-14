# 注意事项（Note）
``在调用前需要您进行操作的事项。``\
``以下项均在Client.py``\
``
What you need to operate before calling.
The following items are in Client.py
``
## 一. 访问域名(Access domain name)
设置您将要访问的域名（HOST）

Set the domain name (HOST) you want to access.
```
        // {endPoint} --> 请求域名(Request domain name)
        aksk_config = BasicConfig()
        aksk_config.end_point = "{endPoint}"
        aksk_config.uri = "xxxxxxx"
        aksk_config.method = "POST"
```

## 二. 请求信息(Request information)
设置 {objName}Request对象 各属性字段值

Set the attribute field values of the {objName}Request object.
```
        {objName}Request.{ParamName} = (value);
```

## 三. 自定义请求信息(Custom request information)
```
// 调用(call)
// json.dumps(${requestFieldName}.to_map()) //可传自定义JSON字符串(can pass custom JSON string)
AkSkAuth.invoke(aksk_config, json.dumps(${requestFieldName}.to_map()))
```

## 四. 账号信息(account information)
设置您的账号和apiKey信息（去除{}）

Set your account and apiKey information (remove {}).
```
        aksk_config.access_key = "{accessKey}"
        aksk_config.secret_key = "{secretKey}"
```

## 五. 如何运行(how to run)
- *Python 版本要求 Python3*(required python 3)
```sh
python setup.py install && python ./Client.py
```

## 六. package缺失的情况(Missing package)
如果使用以上命令发生依赖包缺失的情况，请使用以下命令尝试解决：

If the dependency package is missing when using the above command, resolve it with the following command:
```sh
pip install -i https://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com "requests>=2.10.0" "alibabacloud_tea>=0.3.3,<1.0.0" "alibabacloud_tea_openapi>=0.3.6,<1.0.0" "alibabacloud_tea_console>=0.0.1,<1.0.0" "alibabacloud_tea_util>=0.3.8,<1.0.0"
```
