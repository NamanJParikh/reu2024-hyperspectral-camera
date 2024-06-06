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
  * How does the molten zone affect the growth and the crystal properties?
  * What parts of the images will we care about and how can we isolate them? For example, if we only care about the molten zone, can we automate removing all other parts of the image?
  * What analyses give us the temperature and emissivity coefficients?
    * What parts of these analyses depend on the specific material in the growth, and what parts are general to any material?
    * Can these analyses be automated directly from the images (is it feasible, what tools would it use)?
    * Can we automatically adjust the growth based on analysis of these images as they come in (are the analyses computationally cheap enough to make this possible)?
