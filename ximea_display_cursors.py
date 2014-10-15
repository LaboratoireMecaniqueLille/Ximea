import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import SimpleITK as sitk
from matplotlib.widgets import Slider, Button
rcParams['font.family'] = 'serif'
#ps aux | grep python 					 # KILL python process ...
#kill -9 "insert here the python thread number"		 # ... try it if ximea won't open again.
plt.close('all')

############################## Parameters
nbr_images=1000 # enter here the numer of images you need to save.
save_directory="/home/corentin/Bureau/ximea/" # path to save repository. BE AWARE that this scripts will erase previous images without regrets or remorse.
exposure= 3000 # exposition time, in microseconds
gain=1 
external_trigger= False #set to True if you trig with external source (arduino...). BE AWARE there is a 10s waiting time for the ximea, meaning if you wait more that 10 sec to trigg, ximea will return an error and stop working.
set_FPS=False # set to True if you want to manually set the frame rate. It has 0.1 FPS precison @88FPS . If you need more precision, please use external trigger with arduino.
FPS=50 # set here the frame rate you need. This parameter will only work if set_FPS =True.
##############################

cap = cv2.VideoCapture(cv2.CAP_XIAPI) # open the ximea device

if external_trigger==True:  # this condition activate the trigger mode
  cap.set(cv2.CAP_PROP_XI_TRG_SOURCE,1)
  cap.set(cv2.CAP_PROP_XI_GPI_SELECTOR,1)
  cap.set(cv2.CAP_PROP_XI_GPI_MODE,1)


cap.set(cv2.CAP_PROP_XI_AEAG,0)#auto gain auto exposure
cap.set(cv2.CAP_PROP_XI_DATA_FORMAT,0) #0=8 bits, 1=16(10)bits, 5=8bits RAW, 6=16(10)bits RAW  
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,2048); # reducing this one allows one to increase the FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH,2048);  # doesn't work for this one
#cap.set(cv2.CAP_PROP_XI_DOWNSAMPLING,0) # activate this one if you need to downsample your images, i.e if you need a very high FPS and other options are not enough
#print cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#print cap.get(cv2.CAP_PROP_FRAME_HEIGHT); 


cap.set(cv2.CAP_PROP_EXPOSURE,exposure) # setting up exposure
cap.set(cv2.CAP_PROP_GAIN,gain) #setting up gain
ret, frame = cap.read() # read a frame

### initialising the histogram
if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==0 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==5:
  x=np.arange(0,256,4)
if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==1 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==6:
  x=np.arange(0,1024,4)
hist=np.ones(np.shape(x))

### initialising graph and axes
rat = 0.7
Width=7
Height=7.
fig=plt.figure(figsize=(Height, Width))
axim = fig.add_axes([0.15, 0.135, rat, rat*(Height/Width)]) # Image frame
cax = fig.add_axes([0.17+rat, 0.135, 0.02, rat*(Height/Width)]) # colorbar frame
axhist=fig.add_axes([0.15,(0.17+rat),rat,0.1]) # histogram frame
axhist.set_xlim([0,max(x)]) #set histogram limit in x...
axhist.set_ylim([0,1]) # ... and y

im = axim.imshow(frame,cmap=plt.cm.gray,interpolation='nearest') # display the first image
li,= axhist.plot(x,hist) #plot first histogram
cb = fig.colorbar(im, cax=cax) #plot colorbar
cax.axis('off')


### define cursors here
axcolor = 'lightgoldenrodyellow'
axExp = plt.axes([0.15, 0.02,rat, 0.03], axisbg=axcolor) # define position and size
sExp = Slider(axExp, 'Exposure', 200, 50000, valinit=exposure) #Exposition max = 1000000 # define slider with previous position and size
axGain= plt.axes([0.15, 0.07,rat, 0.03], axisbg=axcolor)
sGain = Slider(axGain, 'Gain', -1, 6, valinit=gain)

def update(val): # this function updates the exposure and gain values 
  cap.set(cv2.CAP_PROP_EXPOSURE,sExp.val)
  cap.set(cv2.CAP_PROP_GAIN,sGain.val)
  fig.canvas.draw_idle()
  
sExp.on_changed(update) # call for update everytime the cursors change
sGain.on_changed(update)



### define buttons here
RECax = plt.axes([0.01, (0.15+rat)/2, 0.05, 0.05]) # define size and position
button = Button(RECax, 'REC', color='red', hovercolor='0.975') # define button

def REC(event): # when called, read "nbr_images" and save them as .tiff in save_directory
  t0=time.time()
  last_t=0
  i=0
  while(i<nbr_images):
    if set_FPS==True and last_t!=0:
      while (time.time()-last_t) < 1./FPS:
	indent=True
    last_t=time.time()
    ret, frame = cap.read()
    image=sitk.GetImageFromArray(frame)
    sitk.WriteImage(image,save_directory+"img_%.5d.tiff" %i) ### works fast in 8 or 16 bit, always use sitk.
    i+=1
  t=time.time()-t0
  print "FPS = %s"%(nbr_images/t)
  
button.on_clicked(REC) # on click, call the REC function


### Main
def get_frame(i):
  ret, frame = cap.read() # read a frame
  if i == 1:
    cax.axis('on')
  im.set_data(frame) #change previous image by new frame
  im.set_clim([frame.min(), frame.max()]) # re-arrange colorbar limits
  histogram=cv2.calcHist([frame],[0],None,[len(x)],[0,max(x)]) # evalute new histogram
  histogram=np.sqrt(histogram)
  li.set_ydata((histogram-histogram.min())/(histogram.max()-histogram.min())) # change previous histogram
  return cax, axim , axhist # return the values that need to be updated



ani = animation.FuncAnimation(fig, get_frame, interval=20, frames=20, blit=False) # This function call the get_frame function to update averything in the figure.
plt.show()