### itchat结合 AI assistant 实现微信小助手

---

# 前言
`代码写的很烂勿喷：`

在csdn看了 [COW AI接入到微信 保姆教程 ](https://blog.csdn.net/m0_69655483/article/details/134170135?spm=1001.2014.3001.5501)大佬的这篇文章后，我也试着部署了一下。  
 部署成功后。我想改进几个方面：   
 		*1.ai与多个好友聊天共享记忆的问题*  
 		*2.与ai对话没有切换声音的选项  语音对话没有情绪 这个Azure的接口可以实现*  
 由于ai assistant可以开启多个线程，实现一个助手和多人聊天分别记忆并长期存储。 于是我尝试使用ai assitant 结合 itchat 实现微信机器人。
    
 	 


---

`提示：这个项目可以在本地运行也可以在服务器运行。只需执行.py主文件就可以了`

# 一、依赖安装

 python必须是3.8.1以上的，我用的3.10.7的  itchat必须是1.5.0.dev才可以,亲测其他itchat版本都不可用    openai必须最新版本。最新版本支持assistant    

  ```python
  pip3 install itchat-uos==1.5.0.dev0  
```
  ```python
 pip3 install --upgrade openai
```
   
# 二、反向代理
由于无法直连ai官网。所以需要构建一个反向代理地址来链接openai api网址
构建方式参考这位大佬的方式[使用Cloudflare创建openai的反向代理](https://blog.csdn.net/guo_zhen_qian/article/details/134957351?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522170442003016777224489813%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=170442003016777224489813&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-1-134957351-null-null.142%5Ev99%5Epc_search_result_base6&utm_term=open%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86&spm=1018.2226.3001.4187)  反向代理创建完成后在代码里这么改即可

```python
client = OpenAI(api_key="你的openai的key", base_url="你的代理地址/v1")
```

# 三、azure注册
如果你没有azure账号，那赶紧注册一个，免费送一年。 注册需要外币信用卡。 动卡空间app可以解决。  azure有免费服务器 免费语音服务都是挺不错的。注册之后通过教程的方法获取语音的key

[Azure注册地址](https://azure.microsoft.com/zh-cn/get-started/welcome-to-azure/?subscriptionId=fb407ffc-43a6-462d-bb96-4ac955ba76c5)

[Azure语音服务使用教程](https://zhuanlan.zhihu.com/p/627165015?utm_id=0)
# 四、执行
先修改config.json文件

命令行运行然后扫码登录即可

```bash
nohup python3 myitchat.py & tail -f nohup.out
```


# 总结
大家可以添加我的小助手微信号来体验一下：
**==ww885087==**


