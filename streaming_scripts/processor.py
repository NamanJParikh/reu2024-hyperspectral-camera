########## Imports ##########

import numpy as np
import pathlib, importlib, logging, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
    UploadDataFile,
)



########## Setup ##########

# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "tutorial_data"
TOPIC_NAME = "tutorial_metadata"

# Path to the root directory of this repo
repo_root_dir = pathlib.Path().resolve().parent

# Paths to the config file and the directory holding the test files
CONFIG_FILE_PATH = repo_root_dir / "streaming_scripts" / "config_files" / "confluent_cloud_broker.config"

# Path to the directory to store the StreamProcessor output
STREAM_PROCESSOR_OUTPUT_DIR = repo_root_dir / "streaming_scripts" / "processor_1"



########## Tasks ##########

class PlaceholderStreamProcessor(DataFileStreamProcessor):
    """Performs a placeholder task (writing out a file to the local system) for every
    data file reconstructed from a topic
    """

    def _process_downloaded_data_file(self, datafile, lock):
        "Writes out a file with a timestamp for each reconstructed file"
        try:
            timestamp = datetime.datetime.now()
            rel_filepath = datafile.relative_filepath
            rel_fp_str = str(rel_filepath.as_posix()).replace("/","_").replace(".","_")
            output_filepath = self._output_dir / f"{rel_fp_str}_placeholder.npy"
            with lock:
                arr = np.array([[1, 2, 3], [4, 5, 6]])
                np.save(output_filepath, arr)
                upload_file = UploadDataFile(output_filepath, rootdir=self._output_dir)
                upload_file.upload_whole_file(CONFIG_FILE_PATH, TOPIC_NAME)
        except Exception as exc:
            return exc
        return None
    
    @classmethod
    def run_from_command_line(cls, args=None):
        "Not used in this example... stay tuned for the live coding tomorrow!"
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
psp = PlaceholderStreamProcessor(
    CONFIG_FILE_PATH,
    CONSUMER_TOPIC_NAME,
    output_dir=STREAM_PROCESSOR_OUTPUT_DIR,
)
# Start running its "process_files_as_read" function in a separate thread
processor_thread = Thread(
    target=stream_processor_task,
    args=(psp,),
)
processor_thread.start()