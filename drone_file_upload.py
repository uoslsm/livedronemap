import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config_drone import BaseConfig as Config
from clients.ldm_client import Livedronemap

image_list = []
eo_list = []

ldm = Livedronemap(Config.LDM_ADDRESS, Config.MAGO3D_ADDRESS)
project_id = ldm.create_project(Config.LDM_PROJECT_NAME)
ldm.set_current_project(Config.LDM_PROJECT_NAME)


def upload_data(image_fname, eo_fname):
    result = ldm.ldm_upload(image_fname, eo_fname)
    print(result)


class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            file_name = event.src_path.split('\\')[-1].split('.')[0]
            file_name_prefix = file_name[0:6]
            extension_name = event.src_path.split('.')[1]
            # FTP 전송시 임시파일 무시하고 다운로드가 완료될 때 까지 대기
            if file_name_prefix == '~ftpb_':
                file_name = file_name[6:]
                while True:
                    time.sleep(1)
                    img_exists = os.path.isfile(
                        os.path.join(Config.DIRECTORY_TO_WATCH, file_name + '.' + Config.IMAGE_FILE_EXT))
                    eo_exists = os.path.isfile(
                        os.path.join(Config.DIRECTORY_TO_WATCH, file_name + '.' + Config.EO_FILE_EXT))
                    if img_exists & eo_exists:
                        break
            if Config.IMAGE_FILE_EXT in extension_name:
                image_list.append(file_name)
            else:
                eo_list.append(file_name)
            for i in range(len(image_list)):
                if image_list[i] in eo_list:
                    upload_data(
                        os.path.join(Config.DIRECTORY_TO_WATCH, file_name + '.' + Config.IMAGE_FILE_EXT),
                        os.path.join(Config.DIRECTORY_TO_WATCH, file_name + '.' + Config.EO_FILE_EXT)
                    )
                    eo_list.remove(image_list.pop(i))


if __name__ == '__main__':
    w = Watcher(directory_to_watch=Config.DIRECTORY_TO_WATCH)
    w.run()
