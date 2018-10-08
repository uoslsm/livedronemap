import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

image_list = []
eo_list = []


class Watcher:
    DIRECTORY_TO_WATCH = "E:\Test_ti"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        print("#### Monitoring Start")
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s" % event.src_path)
            file_name = event.src_path.split('\\')[-1].split('.')[0]
            extension_name = event.src_path.split('.')[1]

            if 'jpg' in extension_name:
                image_list.append(file_name)
            else:
                eo_list.append(file_name)

            for i in range(len(image_list)):
                print(len(image_list))
                if image_list[i] in eo_list:
                    from ldm_client import livedronemap
                    #ldm = livedronemap('http://172.16.127.184:5000/')
                    ldm = livedronemap('http://172.16.127.171:5000/')
                    ldm.create_project('test_ti')
                    ldm.set_current_project('test_ti')
                    print(file_name)
                    ldm.ldm_upload(file_name+'.jpg', file_name+'.txt')
                    #image_list.pop(i)
                    eo_list.remove(image_list.pop(i))
                    #eo_list.pop(eo_list.index(image_list[i]))

        #elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
        #    print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()
