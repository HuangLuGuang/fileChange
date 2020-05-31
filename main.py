# -*- coding: utf-8 -*-
# @createtime    : 2020/5/10 19:28
# @author  : huanglg
# @filename: main.py.py
# @email: luguang.huang@mabotech.com
from watchdog.observers import Observer
import traceback
from watchdog.events import FileSystemEventHandler
from requests.exceptions import ConnectionError
import requests
import time
import os
import json

import constant
from Logger import Logger

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

        url = constant.upload_url
        f = None
        try:
            f = open(file_path, 'rb')
            files = {'pdf': f}
            response = requests.post(url=url, files=files, headers={})
            response.encoding = response.apparent_encoding
            res = json.loads(response.text)
            if isinstance(res, dict) and res['isSuccess'] is False:
                logger.error(response.text.encode('utf-8').decode('unicode_escape'))
                logger.error('文件上传失败：文件路径{}'.format(file_path))
            else:
                logger.info('{}上传成功'.format(file_path))
        except ConnectionError:
            logger.error(traceback.format_exc())
            logger.error('网络中断,{0}：上传失败，已经重试多次！'.format(file_path))
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
        monitor_dir = constant.Monitorfolder
        observer = Observer()
        event_handler = FileEventHandler()
        observer.schedule(event_handler, monitor_dir, True)
        observer.start()
    except FileNotFoundError:
        logger.error("请在桌面新建pdf文件夹")
        time.sleep(5)
        # 重试
        run()

    try:
        while True:
            time.sleep(1)
    except Exception:
        logger.error(traceback.format_exc())
        observer.stop()
    observer.join()

if __name__ == "__main__":

    try:
        logger.info("正常运行中.....")
        run()
    except Exception:
        logger.error(traceback.format_exc())


