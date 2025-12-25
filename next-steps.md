I have, in fact, not finished this code since it didn't run well: there are a multitude of small errors that have been made and need addressing. 

1. curvature function returns a single scalar rather than an array given the norm function without an axis application (to be sorted out by decomposing the numerator and denonmeteror)
2. IMU class (the numerical integration does not do it correctly since it has x += x * dt which doesn't actually make sense)
3. lack of a 'fail-fast' approach to debugging. There are certain things (like the length of `imu_data` which has to remain fixed which I haven't been doing). Therefore, error handling needs to become more of a priority for this project. 
4. 3d autoscale plot needs to be like the implementation in the `spline_interp.ipynb` -- the rest of this is quite minor.