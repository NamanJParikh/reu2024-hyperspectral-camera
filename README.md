# reu2024-hyperspectral-camera
## Planning
### General Parts
* Mount the camera
  * Which furnace will it be mounted on? LDFZ
  * What are the form factor and mounting mechanism of the camera? Tyrel has a mount.
  * Is there any setup (software or hardware) that is needed to get the camera working and collecting images? Hyperspec III
    * How do the people currently using the camera get images?
    * Are they taking single images, automated consecutive frames, etc.? Frame information is recorded in the image's frameIndex file
    * Can this software run on the furnace's built-in computer? Possibly not necessary, we just need to be able to stream the files out where they can be fully analyzed with Python
* Stream the data
  * What system will manage the camera / receive its data? Hyperspec III
  * How to access the camera's output?
  * How is the data formatted? ENVI standard
  * How are images captured (how often, what resolution, etc.)? This information is recorded in the hdr file
  * How to setup OpenMSIStream?
  * How to group / organize the streamed data?
* Consume the data
  * How to visualize and interpret the images? SpectralPy python package
  * What do the images tell us about the molten zone and its properties?
  * How does the molten zone affect the growth and the crystal properties?
  * What parts of the images will we care about and how can we isolate them? For example, if we only care about the molten zone, can we automate removing all other parts of the image?
  * What analyses give us the temperature and emissivity coefficients?
    * What parts of these analyses depend on the specific material in the growth, and what parts are general to any material?
    * Can these analyses be automated directly from the images (is it feasible, what tools would it use)?
    * Can we automatically adjust the growth based on analysis of these images as they come in (are the analyses computationally cheap enough to make this possible)?
   
### Current Steps
* Play with camera and software, take sample images, get data, etc.
  * Take an image with the camera
  * Use the camera's software
  * Get the images into a notebook
    * What is the data format and is it possible to open without the company's app? -- Analysis done using SpectralPy python package
* Look for multi-spectral pyrometry literature - Web of Science database
* Figure out black-body radiation equation and get spectrum from image
* Heat graphite / alumina in standard furnace, take image, and do analysis
