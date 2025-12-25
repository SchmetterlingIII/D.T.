I have, in fact, not finished this code since it didn't run well: there are a multitude of small errors that have been made and need addressing. 

### Physical Design
- upper connector is much too small and design not human centred at all (it will reach onto the neck but is quite bulkly and doesn't spread across well)
- spring calculations to order the correct springs of the right spring constant (as well as how to properly integrate that in a testable chain first)
- foam additions and observations for the design (*although this will take place in quite some time once everything is assembled*)

### Computation
- threading (such that the handling of the data can be done in the background and the animate function can have a fixed FPS)
    - with this comes the ability to export data into a database (for a better understanding of what the data is representing and whether my code is actually outputting what I want (or if there is some difficult to detect error latent somewhere)
- a self-check algorithm (*will I actually learn a little informatics*) to know that whichever filtering algorithm (especially when I move onto kalman later) has settled and its accurate before calibration begins - I have seen that it takes some time before the code rests on a given spline near the beginning (and then it begins to slowly drift as well which I don't like but will counter with kalman)
- having a better output graph (the have an `ax.scatter` for the discrete points of the IMU and make the output just look a little later)

### Maths
- Quaternions (I will not learn it in much detail, but look at how other people have implemented it and learn it in that way (rather than anything fancy)).
- torsion (I will have the display of the results be a bunch of normal vector quivers, whose base is the interpolated position)
- ML (love the idea of ML but not sure how difficult it will be)

### CONCLUSION
To conclude all of this, by the deadline for this project (**January 31st**) all of this code and the physical prototype needs to be completed. 
After this point, I will do a writeup of everything that I have done in a `LaTeX` file that I will accompany when I send off initial cold messages and then more detailed emails (and suggestions for calls) during February and March. I would like to also integrate the work that Lexus has been doing such that I have two selling points for them (so that I actually get this internship): the code and ability to help with the techincalities of this **and** the human-centred aspect (by having interviews and understanding what physiotherapists actually need from such a rehabilitiation device). Then say something on how their work (*knitted textiles rather than bulky IMUs*) is the next step for this (and also maintains their workflow and interests. 

