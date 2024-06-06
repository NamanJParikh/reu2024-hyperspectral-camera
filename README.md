# reu2024-hyperspectral-camera
## Planning
### General Steps and Questions
* Mount the camera
  * Which furnace will it be mounted on?
  * What are the form factor and mounting mechanism of the camera?
  * Is there any setup (software or hardware) that is needed to get the camera working and collecting images?
* Stream the data
  * What system will manage the camera / receive its data?
  * How to access the camera's output?
  * How is the data formatted?
  * How are images captured (how often, what resolution, etc.)?
  * How to setup OpenMSIStream?
  * How to group / organize the streamed data?
* Consume the data
  * How to visualize and interpret the images?
  * What do the images tell us about the molten zone and its properties?
  * What analyses give us the temperature and emissivity coefficients?
    * How computationally expensive are these analyses?
    * Can these analyses be automated directly from the images (using CNNs)?
  * How does the molten zone affect the growth and the crystal properties?
  * What parts of the images will we care about and how can we isolate them? For example, if we only care about the molten zone, can we automate removing all other parts of the image?
  * Can we automatically adjust the growth based on analysis of these images as they come in?
