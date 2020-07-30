# -*- coding: utf-8 -*-
# @createtime    : 2020/5/10 19:28
# @author  : huanglg
# @filename: main.py.py
# @email: luguang.huang@mabotech.com
from watchdog.observers import Observer
import traceback
from watchdog.events import FileSystemEventHandler
from requests.exceptions import ConnectionError
from win32event import CreateMutex
from win32api import GetLastError, MessageBox
from win32con import MB_OK
import requests
import toml
import time
import os
import json

from Logger import Logger

upload_url = "http://10.220.29.28:5000/api/v1/upload_pdf"
device_no = "00001"
logger = Logger()

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print(self.convert_path(event.src_path))
            pdf_path = self.convert_path(event.src_path)
            if 'pdf' in pdf_path.split('.')[-1].lower():
                time.sleep(1)
                print(pdf_path)
                self.upload_pdf(pdf_path)
            logger.info("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))

    def convert_path(self, path: str) -> str:
        seps = r'\/'
        sep_other = seps.replace(os.sep, '')
        return path.replace(sep_other, os.sep) if sep_other in path else path

    def upload_pdf(self, file_path: str):

        f = None
        try:
            f = open(file_path, 'rb')
            files = {'pdf': f}
            data = {"device_no": device_no}
            response = requests.post(url=upload_url, data=data, files=files, headers={})
            response.encoding = response.apparent_encoding
            res = json.loads(response.text)
            if isinstance(res, dict) and res['isSuccess'] is False:
                logger.error(response.text.encode('utf-8').decode('unicode_escape'))
                logger.error('upload filed：file path:{}'.format(file_path))
            else:
                logger.info('{}upload successful'.format(file_path))
        except ConnectionError:
            logger.error(traceback.format_exc())
            logger.error('network connect failed,{0}：upload filed，retry such times！'.format(file_path))
        except PermissionError:
            # 重试
            time.sleep(1)
            self.upload_pdf(file_path)
        finally:
            if f:
                f.close()


def run():
    observer = None
    try:
        # 加载配置文件
        config = toml.load('config.toml')
        monitor_dir = config.get('monitor_folder', os.path.join(os.path.expanduser("~"), 'Desktop', 'pdf'))
        global upload_url, device_no
        upload_url = config.get('upload_url', "http://10.220.29.28:5000/api/v1/upload_pdf")
        device_no = config.get('device_no')
        # 开始监控文件夹
        observer = Observer()
        event_handler = FileEventHandler()
        observer.schedule(event_handler, monitor_dir, True)
        observer.start()
        # 提示运行成功
        logger.info("running.....")
        MessageBox(0, 'The successful running', "info", MB_OK)
    except FileNotFoundError:
        logger.error("please check config file")
        MessageBox(0, 'The Directory not found, please check config file', "error", MB_OK)
        raise

    try:
        while True:
            time.sleep(1)
    except Exception:
        logger.error(traceback.format_exc())
        observer.stop()
    observer.join()

if __name__ == "__main__":

    # 文件互斥，保证运行一次
    mutex = CreateMutex(None, True, 'file_change_mabo_tech')
    last_error = GetLastError()

    if last_error > 0:
        # 如果已经运行给出提示
        MessageBox(0, 'Please do not repeat！', "warning", MB_OK)
    else:
        try:
            run()
        except Exception:
            logger.error(traceback.format_exc())


