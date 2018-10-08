import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

image_list = []
eo_list = []


class Watcher:
    def __init__(self, directory_to_watch, ldm_address, ldm_project_name):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch
        self.ldm_address = ldm_address
        self.ldm_project_name = ldm_project_name

    def run(self):
        event_handler = Handler(self.ldm_address, self.ldm_project_name)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, ldm_address, ldm_project_name):
        Handler.ldm_address = ldm_address
        Handler.ldm_project_name = ldm_project_name
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            file_name = event.src_path.split('\\')[-1].split('.')[0]
            extension_name = event.src_path.split('.')[1]

            if 'jpg' in extension_name:
                image_list.append(file_name)
            else:
                eo_list.append(file_name)

            for i in range(len(image_list)):
                if image_list[i] in eo_list:
                    from ldm_client import livedronemap
                    ldm = livedronemap(Handler.ldm_address)
                    ldm.create_project(Handler.ldm_project_name)
                    ldm.set_current_project(Handler.ldm_project_name)
                    ldm.ldm_upload(file_name+'.jpg', file_name+'.txt')
                    eo_list.remove(image_list.pop(i))


if __name__ == '__main__':
    w = Watcher(
        directory_to_watch='D:\\python-workspace\\livedronemap\\example_upload',
        ldm_address='http://127.0.0.1:5000/',
        ldm_project_name='drone_file_upload_test'
    )
    w.run()
