########## Imports ##########

import numpy as np, matplotlib, matplotlib.pyplot as plt
from io import BytesIO
import pathlib, importlib, logging, datetime, json, platform
from threading import Thread
from openmsitoolbox.logging import OpenMSILogger
from openmsistream import (
    UploadDataFile,
    DataFileUploadDirectory,
    DataFileDownloadDirectory,
    DataFileStreamProcessor,
    MetadataJSONReproducer,
)



########## Setup ##########

matplotlib.use("Agg")

# The name of the topic to work with
TOPIC_NAME = "hyperspec_LDFZ_data"
# The name of the topic to consume files from
CONSUMER_TOPIC_NAME = "hyperspec_LDFZ_result"

# root_dir = pathlib.Path("C:/")
# CONFIG_FILE_PATH = root_dir / "Headwall" / "sensor1" / "broker_configs" / "paradim01_broker.config"
# TEST_FILE_DIR = root_dir / "Headwall" / "sensor1" / "captured"
# STREAM_PROCESSOR_OUTPUT_DIR = root_dir / "Headwall" / "sensor1" / "pyrometry_results"

# Paths to the config file and the directory holding the test files
repo_root_dir = pathlib.Path().resolve().parent
CONFIG_FILE_PATH = repo_root_dir / "StreamingScripts" / "config_files" / "paradim01_broker.config"
TEST_FILE_DIR = repo_root_dir / "StreamingScripts" / "test_folder"

# Path to the directory to store the StreamProcessor output
STREAM_PROCESSOR_OUTPUT_DIR = repo_root_dir / "StreamingScripts" / "processor_2"



########## Tasks ##########

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

class PlaceholderStreamProcessor(DataFileStreamProcessor):
    """Saves the returned temperature array as well as a heatmap plot of it
    """

    def _process_downloaded_data_file(self, datafile, lock):
        try:
            rel_filepath = datafile.relative_filepath
            rel_fp_str = str(rel_filepath.as_posix()).replace("/","_").replace(".","_")
            output_filepath = self._output_dir / f"{rel_fp_str}_result.npy"

            with lock:
                with open(output_filepath, "wb") as filep:
                    filep.write(BytesIO(datafile.bytestring).read())

            temp_arr = np.load(output_filepath, allow_pickle=True)
            plt.figure()
            plt.imshow(temp_arr, cmap="hot")
            plt.colorbar()
            output_filepath = self._output_dir / f"{rel_fp_str}_remade.png"
            plt.savefig(output_filepath)
                
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

if __name__ == "__main__":
    upload_thread.start()
    processor_thread.start()