#################### Imports ####################

import os
import numpy as np, matplotlib.pyplot as plt
import pathlib, logging, importlib, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    UploadDataFile, 
    DataFileUploadDirectory,
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
)



#################### Config ####################

# The name of the topic to produce to
TOPIC_NAME = "tutorial_data"

# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "tutorial_meta_data"

# Path to the root directory of this repo
# repo_root_dir = pathlib.Path().resolve().parent
root_dir = pathlib.Path("C:")

# Paths to the config file and the directory holding the test files
CONFIG_FILE_PATH = root_dir / "Headwall" / "sensor1" / "broker_configs" / "confluent_cloud_broker.config"
DATA_DIR = root_dir / "Headwall" / "sensor1" / "captured"

# Paths to the config file and the directory holding the test files
RESULT_CONFIG_FILE_PATH = root_dir / "Headwall" / "sensor1" / "broker_configs" / "confluent_cloud_broker_for_metadata_consumer.config"
RESULT_FILE_DIR = root_dir / "Headwall" / "sensor1" / "temp_results_arrays"

# Path to the directory to store the StreamProcessor output
STREAM_PROCESSOR_OUTPUT_DIR = root_dir / "Headwall" / "sensor1" / "temp_results_heatmaps"



#################### Tasks ####################

def upload_task(upload_directory, *args, **kwargs):
    """Run "upload_files_as_added" for a given DataFileUploadDirectory, and log a message
    when it gets shut down

    Args:
        upload_directory (DataFileUploadDirectory): the DataFileUploadDirectory to run
        args (list): passed through to "upload_files_as_added"
        kwargs (dict): passed through to "upload_files_as_added"
    """
    # This call to "upload_files_as_added" waits until the program is shut down
    uploaded_filepaths = upload_directory.upload_files_as_added(*args, **kwargs)
    msg = (
        f"The following files were uploaded:\n\t"
    )
    msg += "\n\t".join([str(fp) for fp in uploaded_filepaths])
    upload_directory.logger.info(msg)

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

class ResultPlottingStreamProcessor(DataFileStreamProcessor):
    """Plots and saves the heatmap for every temperature array reconstructed
    from processor stream
    """

    def _process_downloaded_data_file(self, datafile, lock):
        try:
            rel_filepath = datafile.relative_filepath
            rel_fp_str = str(rel_filepath.as_posix()).replace("/","_").replace(".","_")
            output_filepath = self._output_dir / f"{rel_fp_str}_heatmap.png"
            with lock:
                temp_arr = np.load(rel_fp_str)
                plt.figure()
                plt.imshow(temp_arr, cmap='hot')
                plt.savefig(output_filepath)
        except Exception as exc:
            return exc
        return None
    
    @classmethod
    def run_from_command_line(cls, args=None):
        "Not used"
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



#################### Run Producer, Consumer, and Processor ####################

# Create the DataFileUploadDirectory
dfud = DataFileUploadDirectory(
    DATA_DIR, 
    CONFIG_FILE_PATH,
)
# Create separate thread for "upload_files_as_added" function
upload_thread = Thread(
    target=upload_task,
    args=(
        dfud,
        TOPIC_NAME,
    ),
)

# Create the DataFileDownloadDirectory
dfdd = DataFileDownloadDirectory(
    RESULT_FILE_DIR,
    RESULT_CONFIG_FILE_PATH,
    CONSUMER_TOPIC_NAME,
)
# Create separate thread for "reconstruct" function
download_thread = Thread(
    target=download_task,
    args=(dfdd,),
)

# Create the StreamProcessor
psp = ResultPlottingStreamProcessor(
    RESULT_CONFIG_FILE_PATH,
    CONSUMER_TOPIC_NAME,
    output_dir=STREAM_PROCESSOR_OUTPUT_DIR,
)
# Start running its "process_files_as_read" function in a separate thread
processor_thread = Thread(
    target=stream_processor_task,
    args=(psp,),
)

# Start running the threads
upload_thread.start()
download_thread.start()
processor_thread.start()