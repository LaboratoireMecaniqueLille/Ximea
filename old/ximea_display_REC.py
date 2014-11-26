import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import SimpleITK as sitk
from multiprocessing import Process, Pipe, Value
from matplotlib.widgets import Slider, Button
rcParams['font.family'] = 'serif'
#ps aux | grep python 					 # KILL python process ...
#kill -9 insert_here_the_python_thread_number		 # ... try it if ximea won't open again.
plt.close('all')

############################## Parameters
nbr_images=400 # enter here the numer of images you need to save.
save_directory="/home/corentin/Bureau/ximea/" # path to save repository. BE AWARE that this scripts will erase previous images without regrets or remorse.
exposure= 10000 # exposition time, in microseconds
gain=2
height=1024 # reducing this one allows one to increase the FPS
width=1024 # doesn't work for this one
data_format=6 #0=8 bits, 1=16(10)bits, 5=8bits RAW, 6=16(10)bits RAW  
external_trigger= False #set to True if you trig with external source (arduino...). BE AWARE there is a 10s waiting time for the ximea, meaning if you wait more that 10 sec to trigg, ximea will return an error and stop working.
set_FPS=False # set to True if you want to manually set the frame rate. It has 0.1 FPS precison @88FPS . If you need more precision, please use external trigger with arduino.
FPS=50 # set here the frame rate you need. This parameter will only work if set_FPS =True.
numdevice = 0 # Set the number of the camera (if several cameras plugged)
##############################

rec_send , rec_recv = Pipe()
anim_send, anim_recv = Pipe()
rec_signal=Value('i',0)
plot_signal=Value('i',0)

#cap = cv2.VideoCapture(cv2.CAP_XIAPI) # open the ximea device
#cap = cv2.VideoCapture(cv2.CAP_XIAPI + numdevice) # open the ximea device Ximea devices start at 1100. 1100 => device 0, 1101 => device 1 

#if external_trigger==True:  # this condition activate the trigger mode
  #cap.set(cv2.CAP_PROP_XI_TRG_SOURCE,1)
  #cap.set(cv2.CAP_PROP_XI_GPI_SELECTOR,1)
  #cap.set(cv2.CAP_PROP_XI_GPI_MODE,1)

#cap.set(cv2.CAP_PROP_XI_DATA_FORMAT,data_format) #0=8 bits, 1=16(10)bits, 5=8bits RAW, 6=16(10)bits RAW  

#if data_format ==1 or data_format==6: #increase the FPS in 10 bits
  #cap.set(cv2.CAP_PROP_XI_OUTPUT_DATA_BIT_DEPTH,10)
  #cap.set(cv2.CAP_PROP_XI_DATA_PACKING,1)


#cap.set(cv2.CAP_PROP_XI_AEAG,0)#auto gain auto exposure
#cap.set(cv2.CAP_PROP_FRAME_WIDTH,width);  # doesn't work for this one
##cap.set(cv2.CAP_PROP_XI_OFFSET_X,640);
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height); # reducing this one allows one to increase the FPS
##cap.set(cv2.CAP_PROP_XI_DOWNSAMPLING,0) # activate this one if you need to downsample your images, i.e if you need a very high FPS and other options are not enough
##print cap.get(cv2.CAP_PROP_FRAME_WIDTH)
##print cap.get(cv2.CAP_PROP_FRAME_HEIGHT); 

#cap.set(cv2.CAP_PROP_EXPOSURE,exposure) # setting up exposure
#cap.set(cv2.CAP_PROP_GAIN,gain) #setting up gain
#ret, frame = cap.read() # read a frame

### initialising the histogram
#if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==0 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==5:
  #x=np.arange(0,256,4)
#if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==1 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==6:
  #x=np.arange(0,1024,4)
#hist=np.ones(np.shape(x))

### initialising graph and axes
rat = 0.7
Width=7
Height=7.

rat = 0.7
Width=7
Height=7.
fig=plt.figure(figsize=(Height, Width))
frame=np.zeros((height,width))
axim = fig.add_axes([0.15, 0.135, rat, rat*(Height/Width)]) # Image frame
im = axim.imshow(frame,cmap=plt.cm.gray,interpolation='nearest') # display the first image
RECax = plt.axes([0.01, (0.15+rat)/2, 0.05, 0.05]) # define size and position
button = Button(RECax, 'REC', color='red', hovercolor='0.975') # define button
#fig=plt.figure(figsize=(Height, Width))
#ax=fig.add_subplot(111)
##axim = fig.add_axes([0.15, 0.135, rat, rat*(Height/Width)]) # Image frame
##cax = fig.add_axes([0.17+rat, 0.135, 0.02, rat*(Height/Width)]) # colorbar frame
##axhist=fig.add_axes([0.15,(0.17+rat),rat,0.1]) # histogram frame
##axhist.set_xlim([0,max(x)]) #set histogram limit in x...
##axhist.set_ylim([0,1]) # ... and y
#frame=np.zeros((height,width))
#im = ax.imshow(frame,cmap=plt.cm.gray,interpolation='nearest') # display the first image
##li,= axhist.plot(x,hist) #plot first histogram
##cb = fig.colorbar(im, cax=cax) #plot colorbar
##cax.axis('off')
#fig.canvas.draw() 
#plt.show(block=False)


### define cursors here
#axcolor = 'lightgoldenrodyellow'
#axExp = plt.axes([0.15, 0.02,rat, 0.03], axisbg=axcolor) # define position and size
#sExp = Slider(axExp, 'Exposure', 200, 50000, valinit=exposure) #Exposition max = 1000000 # define slider with previous position and size
#axGain= plt.axes([0.15, 0.07,rat, 0.03], axisbg=axcolor)
#sGain = Slider(axGain, 'Gain', -1, 6, valinit=gain)

#def update(val): # this function updates the exposure and gain values 
  #cap.set(cv2.CAP_PROP_EXPOSURE,sExp.val)
  #cap.set(cv2.CAP_PROP_GAIN,sGain.val)
  #fig.canvas.draw_idle()
  
#sExp.on_changed(update) # call for update everytime the cursors change
#sGain.on_changed(update)



### define buttons here
#RECax = plt.axes([0.01, (0.15+rat)/2, 0.05, 0.05]) # define size and position
#button = Button(RECax, 'REC', color='red', hovercolor='0.975') # define button

def REC(): # when called, read "nbr_images" and save them as .tiff in save_directory
  while True:
    while rec_signal.value!=1:
      indent=True
    t0=time.time()
    last_t=0
    i=0
    while(i<nbr_images):
      if set_FPS==True and last_t!=0: #This loop is used to set the FPS
	while (time.time()-last_t) < 1./FPS:
	  indent=True
      last_t=time.time()
      frame = rec_recv.recv()
      image=sitk.GetImageFromArray(frame)
      sitk.WriteImage(image,save_directory+"img_%.5d.tiff" %i) ### works fast in 8 or 16 bit, always use sitk.
      i+=1
    rec_signal.value=0
    t=time.time()-t0
    print "FPS = %s"%(nbr_images/t)
  

#def REC_one(event): # when called, read 1 image and save it as .tiff in save_directory with a timestamp, so the next REC will not erase the previous one
  #ret, frame = cap.read()
  #image=sitk.GetImageFromArray(frame)
  #sitk.WriteImage(image,save_directory+"img_%.5d.tiff" %(time.time())) ### works fast in 8 or 16 bit, always use sitk.
  
def REC2(event):
  rec_signal.value=1

  
#button.on_clicked(REC2) # on click, call the REC function


### Main

def function(i):
  print "function aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  plot_signal.value=1
  frame=anim_recv.recv() # read a frame
  plot_signal.value=0
  print "received!"
  print frame[0]
  im.set_data(frame) 
  return axim


def get_frame():
  cap = cv2.VideoCapture(cv2.CAP_XIAPI + numdevice) # open the ximea device Ximea devices start at 1100. 1100 => device 0, 1101 => device 1 

  if external_trigger==True:  # this condition activate the trigger mode
    cap.set(cv2.CAP_PROP_XI_TRG_SOURCE,1)
    cap.set(cv2.CAP_PROP_XI_GPI_SELECTOR,1)
    cap.set(cv2.CAP_PROP_XI_GPI_MODE,1)

  cap.set(cv2.CAP_PROP_XI_DATA_FORMAT,data_format) #0=8 bits, 1=16(10)bits, 5=8bits RAW, 6=16(10)bits RAW  

  if data_format ==1 or data_format==6: #increase the FPS in 10 bits
    cap.set(cv2.CAP_PROP_XI_OUTPUT_DATA_BIT_DEPTH,10)
    cap.set(cv2.CAP_PROP_XI_DATA_PACKING,1)

  cap.set(cv2.CAP_PROP_XI_AEAG,0)#auto gain auto exposure
  cap.set(cv2.CAP_PROP_FRAME_WIDTH,width);  # doesn't work for this one
  #cap.set(cv2.CAP_PROP_XI_OFFSET_X,640);
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height); # reducing this one allows one to increase the FPS
  #cap.set(cv2.CAP_PROP_XI_DOWNSAMPLING,0) # activate this one if you need to downsample your images, i.e if you need a very high FPS and other options are not enough
  #print cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  #print cap.get(cv2.CAP_PROP_FRAME_HEIGHT); 

  cap.set(cv2.CAP_PROP_EXPOSURE,exposure) # setting up exposure
  cap.set(cv2.CAP_PROP_GAIN,gain) #setting up gain
  while True:
    ret, frame=cap.read()
    print "this is Patrick"
    print frame[0]
    print plot_signal.value
    if plot_signal.value==1:
      anim_send.send(frame)
      print "sended"
    print rec_signal.value
    if rec_signal.value==1:
      rec_send.send(frame)
      


      
Get_frame=Process(target=get_frame,args=())
time.sleep(1)
#Rec=Process(target=REC,args=())
#Ani=Process(target=ani,args=())


Get_frame.start()
time.sleep(1)
#Ani.start()
#Rec.start()

#ani = animation.FuncAnimation(fig, anim, interval=20, frames=20, blit=False) # This function call the anim function to update averything in the figure.
#plt.show()
Get_frame.join()
time.sleep(1)
#Ani.join()
animation.FuncAnimation(fig, function, interval=20, frames=20, blit=False) # This function call the anim function to update averything in the figure.
plt.show()
#Rec.join()


