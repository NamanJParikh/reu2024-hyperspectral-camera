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

# Path to the directory to store the reconstructed data
RECO_DIR = repo_root_dir / "streaming_scripts" / "image_reco"



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

if __name__ == "__main__": download_thread.start()