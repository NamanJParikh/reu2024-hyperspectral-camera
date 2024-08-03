########## Imports ##########

import numpy as np
from time import sleep
import pathlib, importlib, logging, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
    UploadDataFile,
)
import sys, os
sys.path.append(os.path.abspath("/home/nparik15/"))
# sys.path.append(os.path.abspath("/Users/namanparikh/Documents/GitHub/paradim/reu2024-hyperspectral-camera"))
import temperature_analysis



########## File Tracking ##########

class FolderTracker():
    def __init__(self):
        self.analyzed = False
        self.dict = {
            "whiteReference": False,
            "whiteReference.hdr": False,
            "darkReference": False,
            "darkReference.hdr": False,
            "data": False,
            "data.hdr": False,
            "raw": False,
            "raw.hdr": False,
            "frameIndex.txt": False
        }

    def update(self, filename):
        if filename in self.dict.keys(): self.dict[filename] = True

    def is_ready(self):
        return (
            self.dict["whiteReference"]
            and self.dict["whiteReference.hdr"]
            and self.dict["darkReference"]
            and self.dict["darkReference.hdr"]
            and self.dict["data"]
            and self.dict["data.hdr"]
            and self.dict["raw"]
            and self.dict["raw.hdr"]
            and self.dict["frameIndex.txt"]
        )

    def mark_analyzed(self):
        self.analyzed = True
    
    def is_analyzed(self):
        return self.analyzed

GlobalTracker = dict()



########## Setup ##########

# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "hyperspec_LDFZ_data"
TOPIC_NAME = "hyperspec_LDFZ_result"

# # Path to the root directory of this repo
# repo_root_dir = pathlib.Path().resolve().parent

# # Paths to the config file and the directory holding the test files
# CONFIG_FILE_PATH = repo_root_dir / "StreamingScripts" / "config_files" / "paradim01_broker.config"

# # Path to the directory to store the reconstructed data
# STREAM_PROCESSOR_OUTPUT_DIR = repo_root_dir / "StreamingScripts" / "processor_1"

root_dir = pathlib.Path("/home/nparik15/")
CONFIG_FILE_PATH = root_dir / "config_files" / "paradim01_broker.config"
STREAM_PROCESSOR_OUTPUT_DIR = root_dir / "hyperspec_LDFZ_data"



########## Tasks ##########

class ImageAnalysisProcessor(DataFileStreamProcessor):
    """Performs a placeholder task (writing out a file to the local system) for every
    data file reconstructed from a topic
    """

    def _process_downloaded_data_file(self, datafile, lock):
        "Runs temperature analysis of image when all needed files have been streamed"
        try:
            # construct output paths
            rel_filepath = datafile.relative_filepath
            rel_fp_str = str(rel_filepath.as_posix())

            folder = rel_fp_str[:rel_fp_str.rfind("/")]
            folderpath = str(self._output_dir / folder)
            file = rel_fp_str[rel_fp_str.rfind("/")+1:]
            output_filepath = self._output_dir / folder / "result.npy"

            print(folder, file)

            with lock:
                # check if all files have arrived 
                # and that image has not already been analyzed
                if folder not in GlobalTracker.keys():
                    GlobalTracker[folder] = FolderTracker()

                (GlobalTracker[folder]).update(file)

                if (GlobalTracker[folder]).is_analyzed():
                    return None
                if (GlobalTracker[folder]).is_ready():
                    # perform analysis and upload result
                    temp_arr = temperature_analysis.analysis(folderpath)
                    np.save(output_filepath, temp_arr, allow_pickle=True)
                    upload_file = UploadDataFile(output_filepath, rootdir=self._output_dir)
                    upload_file.upload_whole_file(CONFIG_FILE_PATH, TOPIC_NAME)

                    GlobalTracker[folder].mark_analyzed()

        except Exception as exc:
            return exc
        return None
    
    @classmethod
    def run_from_command_line(cls, args=None):
        pass

def stream_processor_task(stream_processor):
    """Run "process_files_as_read" for the given stream processor, and log a message
    when it gets shuts down
    
    Args:
        stream_processor (openmsistream.DataFileStreamProcessor): The stream processor to run
    """
    # This call to "process_files_as_read" hangs until the stream processor is shut down
    (
        n_m_r, # The number of messages read
        n_m_p, # The number of messages processed
        n_f_p, # The number of files successfully processed
        p_fps, # Paths to the most recently-processed files
    ) = stream_processor.process_files_as_read()
    stream_processor.close()
    msg = f"{n_m_r} total messages were consumed"
    if n_f_p > 0:
        msg += (
            f", {n_m_p} messages were processed,"
            f" and {n_f_p} files were successfully processed"
        )
    else:
        msg += f" and {n_m_p} messages were successfully processed"
    msg += (
        f". Up to {stream_processor.N_RECENT_FILES} most recently "
        "processed files:\n\t"
    )
    msg += "\n\t".join([str(fp) for fp in p_fps])
    stream_processor.logger.info(msg)



########## Run ##########

# Create the StreamProcessor
iap = ImageAnalysisProcessor(
    config_file=CONFIG_FILE_PATH,
    topic_name=CONSUMER_TOPIC_NAME,
    output_dir=STREAM_PROCESSOR_OUTPUT_DIR,
    mode="disk"
)
# Start running its "process_files_as_read" function in a separate thread
processor_thread = Thread(
    target=stream_processor_task,
    args=(iap,),
)

if __name__ == "__main__": 
    processor_thread.start()

    # Periodically remove analyzed images from the tracker
    while True:
        sleep(86400)
        for key in GlobalTracker.keys():
            if GlobalTracker[key].is_analyzed():
                del GlobalTracker[key]
