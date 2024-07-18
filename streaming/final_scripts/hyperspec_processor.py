#################### Imports ####################

import numpy as np
import pathlib, importlib, logging, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
    DataFileStreamReproducer,
)
from openmsistream.data_file_io import ReproducerMessage, DataFile



#################### Tasks ####################

class HyperspectralImageProcessor(DataFileStreamReproducer):
    """Analyzes hyperpectral image and returns a file of the temperature array
    """

    def _get_processing_result_message_for_file(self, datafile, lock):
        try:
            rel_filepath = datafile.relative_filepath
            rel_fp_str = str(rel_filepath.as_posix()).replace("/","_").replace(".","_")
            output_filepath = self._output_dir / f"{rel_fp_str}_result.npy"
            with lock:
                np.save(output_filepath, np.zeros((3,3), dtype=np.int64))
        except:
            return None
        return ReproducerMessage(DataFile(output_filepath))
    
    @classmethod
    def run_from_command_line(cls, args=None):
        "Not used"
        pass

def reproducer_task(reproducer):
    """Run "produce_processing_results_for_files_as_read" for a given
    DataFileStreamReproducer, and log some messages when it gets shut down

    Args:
        reproducer (DataFileStreamReproducer): the DataFileStreamReproducer to run
    """
    # This call to "produce_processing_results_for_files_as_read" hangs until the program
    # is shut down
    (
        n_m_r, # number of messages read
        n_m_p, # number of messages processed
        n_f_r, # number of files read
        n_f_mp, # number of files that had metadata produced
        m_p_fps, # paths to files that had metadata produced (up to 50)
    ) = reproducer.produce_processing_results_for_files_as_read()
    reproducer.close()
    # Create a log a message stating the files that were processed during the run
    msg = ""
    if n_m_r > 0:
        msg += f'{n_m_r} total message{"s were" if n_m_r!=1 else " was"} consumed, '
    if n_m_p > 0:
        msg += f'{n_m_p} message{"s were" if n_m_p!=1 else " was"} successfully processed, '
    if n_f_r > 0:
        msg += f'{n_f_r} file{"s were" if n_f_r!=1 else " was"} fully read, '
    if n_f_mp > 0:
        msg += (
            f'{n_f_mp} file{"s" if n_f_mp!=1 else ""} had json metadata produced '
            f'to the "{reproducer.producer_topic_name}" topic. '
            f"Up to {reproducer.N_RECENT_FILES} most recent:\n\t"
        )
    msg += "\n\t".join([str(fp) for fp in m_p_fps])
    reproducer.logger.info(msg)



#################### Config ####################

# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "tutorial_data"

# Path to the root directory of this repo
repo_root_dir = pathlib.Path().resolve().parent

# Path to the config file to use for the Reproducer
REPRODUCER_CONFIG_FILE_PATH = (
    repo_root_dir / "streaming" / "config_files" / "confluent_cloud_broker_for_reproducer.config"
)

# Path to the directory to store the Reproducer registry files
REPRODUCER_OUTPUT_DIR = repo_root_dir / "streaming" / "Reproducer_output"

# Name of the topic to produce the metadata messages to
PRODUCER_TOPIC_NAME = "tutorial_metadata"



#################### Run Reproducer ####################

# Create the ImageProcessor
hip = HyperspectralImageProcessor(
    REPRODUCER_CONFIG_FILE_PATH,
    CONSUMER_TOPIC_NAME,
    PRODUCER_TOPIC_NAME,
    output_dir=REPRODUCER_OUTPUT_DIR,
)
# Start running its "produce_processing_results_for_files_as_read" function in a separate thread
reproducer_thread = Thread(
    target=reproducer_task,
    args=(hip,),
)
reproducer_thread.start()