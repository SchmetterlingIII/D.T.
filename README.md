# D.T.
The coded aspects of my A-Level D.T. courework, in which I am designing a posture correction device aimed at heightening the awareness of users through haptic feedback and continual monitoring. My aim is to encourage user awareness of their posture and thus user autonomy on how they should approach treatments/exercises - hoping to alleviate the stress on healthcare systems by providing a preventative solution to spinal monitoring. 

This project aims to reconstruct the shape of the human spine and monitor posture in real-time using data from Inertial Measurement Units (IMUs) connected via an Arduino. The shape is estimated using cubic spline interpolation based on sensor positions derived from accelerometer data.

The system includes a calibration phase to establish a baseline "good" posture and subsequently detects deviations from this baseline by analyzing the curvature ($\kappa$) of the interpolated spline. Deviations are identified, localized to specific sensor segments, and signaled via serial output; eventually for haptic feedback and data logging (SQLite).

The output from this includes 3D visualization of the sensor positions and spline, and 2D plotting of the curvature. *This will be improved with a more accurate digital twin of the spine by not restricting myself to cubic interpolation*.

Below is my most recent render of this, using Fusion360:
![alt text](image.png)

*This project serves as a proof of concept and developments to it should be:*
- Moving towards B-spline interpolation (in which the parameters can be more fine-tuned)
- Using quaternions to handle the tilt (to avoid gimbal lock)
- Implementation of sensor fusion (with both accelerometer and gyroscope data)
- Integration of haptic motors for user feedback

Further, I would be interested in the embedding of sensors this within textile technology (like the textiles in *Imperial's e-Body Lab*) so that they can discretely be integrated into clothing: this approach would require the conversion of stress within these sensors to curvature. 