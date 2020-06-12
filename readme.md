#### 三坐标测量机文件监控
##### 打包成可执行文件exe
``` shell script
    pyinstaller -F main.py

    可以修改main.spec文件，保留配置文件
  
   -D  –onedir 创建一个目录，包含 exe 文件，但会依赖很多文件（默认选项）。

    -w 表示去掉控制台窗口，这在 GUI 界面时非常有用。不过如果是命令行程序的话那就把这个选项删除吧！；

    -c  –console, –nowindowed 使用控制台，无界面 (默认)；

    -p 表示你自己自定义需要加载的类路径，一般情况下用不到；

    -i 表示可执行文件的图标。
```

1.在constant.py里配置一下要监控的文件路径

2.配置自启，创建main.exe的快捷方式，将快捷方式复制到 %programdata%\Microsoft\Windows\Start Menu\Programs\Startup 



