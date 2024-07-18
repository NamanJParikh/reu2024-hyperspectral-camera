# imports
import datetime
import pathlib, logging, importlib
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
    UploadDataFile, 
    DataFileUploadDirectory,
)


# The name of the topic to work with
TOPIC_NAME = "tutorial_data"

# Paths to the config file and the directory holding the test files
repo_root_dir = pathlib.Path().resolve().parent
CONFIG_FILE_PATH = repo_root_dir / "config_files" / "confluent_cloud_broker.config"
TEST_FILE_DIR = repo_root_dir.parent / "final_scripts" / "test_camera_capture"

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

# Create the DataFileUploadDirectory
dfud = DataFileUploadDirectory(TEST_FILE_DIR, CONFIG_FILE_PATH)
# Start running its "upload_files_as_added" function in a separate thread
upload_thread = Thread(
    target=upload_task,
    args=(
        dfud,
        TOPIC_NAME,
    ),
)
upload_thread.start()


# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "tutorial_metadata"

# Path to the root directory of this repo
repo_root_dir = pathlib.Path().resolve().parent

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
            output_filepath = self._output_dir / f"{rel_fp_str}_placeholder.txt"
            with lock:
                with open(output_filepath, "w") as filep:
                    filep.write(
                        f"Processing timestamp: {timestamp.strftime('%m/%d/%Y, %H:%M:%S')}"
                    )
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

# Path to the directory to store the StreamProcessor output
STREAM_PROCESSOR_OUTPUT_DIR = repo_root_dir / "final_scripts"  / "PlaceholderStreamProcessor_output"

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