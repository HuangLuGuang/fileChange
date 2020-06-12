# -*- coding: utf-8 -*-
# @createTime    : 2020/6/1 17:30
# @author  : Huanglg
# @fileName: test.py
# @email: luguang.huang@mabotech.com

# -*- coding: utf-8 -*-
import json
import os, threading
import time
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import *
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, aim_path):
        FileSystemEventHandler.__init__(self)
        self.aim_path = aim_path
        self.timer = None
        self.snapshot = DirectorySnapshot(self.aim_path)

    def on_any_event(self, event):
        if self.timer:
            self.timer.cancel()

        self.timer = threading.Timer(0.2, self.checkSnapshot)
        self.timer.start()

    def checkSnapshot(self):
        snapshot = DirectorySnapshot(self.aim_path)
        diff = DirectorySnapshotDiff(self.snapshot, snapshot)
        self.snapshot = snapshot
        self.timer = None

        # diff.files_created
        # diff.files_deleted
        # diff.files_modified
        # diff.files_moved
        # diff.dirs_modified
        # diff.dirs_moved
        # diff.dirs_deleted
        # diff.dirs_created
        if diff.files_modified:
            print(diff.files_modified[0])
            path_file = diff.files_modified[0]
            last_line = self.get_last_line(path_file).decode('utf-8').rstrip()
            print(last_line)
            text_list = last_line.split(',')
            result = {
                'test_date': text_list[0],
                'serial_no': text_list[4],
                'test_attribute': text_list[5],
                'rotate': text_list[6],
                'dynamic_balance1': self.handler_dynamic_balance(text_list[7]),
                'angle1': int(float(text_list[8]) + 0.5),
                'dynamic_balance2': self.handler_dynamic_balance(text_list[9]),
                'angle2': int(float(text_list[10]) + 0.5)
            }
            print(text_list)
            print(result)

    @staticmethod
    def handler_dynamic_balance(value):
        list_value = list(value)
        list_value.insert(2, '.')
        str_value = ''.join(list_value)
        float_value = '%.1f' % float(str_value)
        return float_value

    def get_last_line(self, filename):
        """
        get last line of a file
        :param filename: file name
        :return: last line or None for empty file
        """
        try:
            filesize = os.path.getsize(filename)
            if filesize == 0:
                return None
            else:
                with open(filename, 'rb') as fp:  # to use seek from end, must use mode 'rb'
                    offset = -8  # initialize offset
                    while -offset < filesize:  # offset cannot exceed file size
                        fp.seek(offset, 2)  # read # offset chars from eof(represent by number '2')
                        lines = fp.readlines()  # read from fp to eof
                        if len(lines) >= 2:  # if contains at least 2 lines
                            return lines[-1]  # then last line is totally included
                        else:
                            offset *= 2  # enlarge offset
                    fp.seek(0)
                    lines = fp.readlines()
                    return lines[-1]
        except FileNotFoundError:
            print(filename + ' not found!')
            return None
        except PermissionError:
            time.sleep(1)
            self.get_last_line(filename)


class DirMonitor(object):
    """文件夹监视类"""

    def __init__(self, aim_path):
        """构造函数"""

        self.aim_path = aim_path
        self.observer = Observer()

    def start(self):
        """启动"""

        event_handler = FileEventHandler(self.aim_path)
        self.observer.schedule(event_handler, self.aim_path, True)
        self.observer.start()

    def stop(self):
        """停止"""

        self.observer.stop()


if __name__ == "__main__":
    monitor = DirMonitor(r"F:\\edgeComputer\\fileChange\\example")
    try:
        monitor.start()
        while True:
            time.sleep(1)
    except Exception:
        monitor.stop()
