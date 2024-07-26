########## Imports ##########

import numpy as np
import os, pathlib, importlib, logging, time, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
    UploadDataFile,
)
from watchdog.events import (
    FileCreatedEvent,
    DirCreatedEvent,
)
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import temperature_analysis

########## Setup ##########

# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "hyperspec_LDFZ_data"
TOPIC_NAME = "hyperspec_LDFZ_result"

# root_dir = pathlib.Path("/home/nparik15/")
# CONFIG_FILE_PATH = root_dir / "config_files" / "paradim01_broker.config"
# RECO_DIR = root_dir / "hyperspec_LDFZ_data"

# Path to the root directory of this repo
repo_root_dir = pathlib.Path().resolve().parent

# Paths to the config file and the directory holding the test files
CONFIG_FILE_PATH = repo_root_dir / "streaming_scripts" / "config_files" / "paradim01_broker.config"

# Path to the directory to store the reconstructed data
RECO_DIR = repo_root_dir / "streaming_scripts" / "image_reco"

# # Path to the director to store temperature arrays resulting from analysis
# ANALYSIS_DIR = repo_root_dir / "streaming_scripts" / "processor_1"



########## Tasks ##########

def download_task(download_directory):
    """Run "reconstruct" for a given DataFileDownloadDirectory, and log some messages
    when it gets shut down

    Args:
        download_directory (DataFileDownloadDirectory): the DataFileDownloadDirectory to run
    """
    # This call to "reconstruct" waits until the program is shut down
    (
        n_read,
        n_processed,
        n_complete_files,
        complete_filepaths,
    ) = download_directory.reconstruct()
    download_directory.close()
    msg = f"{n_read} total messages were consumed"
    if len(complete_filepaths) > 0:
        msg += (
            f", {n_processed} messages were successfully processed, and "
            f'{n_complete_files} file{" was" if n_complete_files==1 else "s were"} '
            "successfully reconstructed"
        )
    else:
        msg += f" and {n_processed} messages were successfully processed"
    msg += (
        f". Most recent completed files (up to {download_directory.N_RECENT_FILES}):\n\t"
    )
    msg += "\n\t".join([str(filepath) for filepath in complete_filepaths])
    download_directory.logger.info(msg)

class Watcher:
    def __init__(self, path, handler):
        self.observer = Observer()
        self.watch_directory = path
        self.handler = handler

    def run(self):
        self.observer.schedule(self.handler, self.watch_directory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(3)
        except:
            self.observer.stop()
            print("Observer Stopped")
 
        self.observer.join()

# def analysis(folder_path): return np.array([[1, 2], [3, 4], [5, 6]])

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if event.src_path[-4:] == ".npy" or event.src_path[-4:] == ".log":
            return
        if isinstance(event, DirCreatedEvent):
            print(f"Watchdog found {event.src_path} directory created...")
            rootdir = event.src_path
            print(f"Root directory {rootdir}")
            files = os.listdir(rootdir)
            print(f"Files {files}")
        elif isinstance(event, FileCreatedEvent):
            print(f"Watchdog handling {event.src_path} file created...")
            rootdir = os.path.dirname(event.src_path)
            print(f"Root directory {rootdir}")
            files = os.listdir(rootdir)
            print(f"Files {files}")
        else: return

        foldername = rootdir[rootdir.rfind("/")+1:]
        print(foldername)
        output_filepath = rootdir + "/" + foldername + ".npy"

        if not (
            "whiteReference" in files
            and "whiteReference.hdr" in files
            and "darkReference" in files
            and "darkReference.hdr" in files
            and "raw" in files
            and "raw.hdr" in files
            and "data" in files
            and "data.hdr" in files
            and "frameIndex.txt" in files
            and foldername + ".npy" not in files
        ): return

        folder_path = str(RECO_DIR / foldername)
        temp_arr = "FAIL"
        while type(temp_arr) == str:
            temp_arr = temperature_analysis.analysis(folder_path)
        
        np.save(output_filepath, temp_arr, allow_pickle=True)
        upload_file = UploadDataFile(pathlib.Path(output_filepath), rootdir=rootdir)
        upload_file.upload_whole_file(CONFIG_FILE_PATH, TOPIC_NAME)



########## Run ##########

# Create the DataFileDownloadDirectory
dfdd = DataFileDownloadDirectory(
    RECO_DIR,
    CONFIG_FILE_PATH,
    CONSUMER_TOPIC_NAME,
)
# Start running its "reconstruct" function in a separate thread
download_thread = Thread(
    target=download_task,
    args=(dfdd,),
)

if __name__ == "__main__": 
    download_thread.start()
    watcher = Watcher(RECO_DIR, Handler())
    watcher.run()