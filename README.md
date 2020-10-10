# Advanced Lane Finding

## Project code 
The code is devided in a [library](./lib.py) and an [IPython Notebook](./find_lanelines.ipynb). The [Notebook](./find_lanelines.ipynb) contains all information to understand the code structure on a high level. It also describes why I chose to use what functions, thresholds and algorithms in what order. My explanations are quite brief, because I think that a computer vision project should be explained with images rather than with words. That is why I provided an image for every processing step, showing the effect and necessity of the step.

The [library](./lib.py) contains mostly functions from the classroom with some modifications done by me. It also includes some helper functions. I decided to have almost all functions in the [library](./lib.py), because it makes the [Notebook](./find_lanelines.ipynb) nice and readable. The only function I kept in the [Notebook](./find_lanelines.ipynb) was the one that combines all processing steps taking a raw frame and returning an undistorted frame showing the lane, curvature radius and displacement. 

The result can be seen in [project_output.mp4](./project_output.mp4).

## Discussion
My image processing pipeline works quite well, but it produces lines, that sometimes jiggle a bit, especially in areas with a bright surface. This can be improved by implementing robustness measures, i.e. interpolating results from more than one frame. This would lead to smoothing of outputs. Also outliers could be detected more easily like that and thus be ignored. 

On straight parts of the highway the results for the curvature radius jiggles a lot. I assume though, that that is because the radius goes towards infinity on straight lines. 
