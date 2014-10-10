import numpy as np
import cv2
import time
import skimage.io as io
io.use_plugin('freeimage')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import SimpleITK as sitk
from matplotlib.widgets import Slider, Button


rcParams['font.family'] = 'serif'
#ps aux | grep python  #### KILL python process
plt.close('all')

cap = cv2.VideoCapture(cv2.CAP_XIAPI)

############################### Activate the following to enable external trigger
cap.set(cv2.CAP_PROP_XI_TRG_SOURCE,1)
cap.set(cv2.CAP_PROP_XI_GPI_SELECTOR,1)
cap.set(cv2.CAP_PROP_XI_GPI_MODE,1)
###############################

cap.set(cv2.CAP_PROP_XI_AEAG,0)#auto gain auto exposure
cap.set(cv2.CAP_PROP_XI_DATA_FORMAT,0) #0=8 bits, 1=16(10)bits, 5=8bits RAW, 6=16(10)bits RAW  
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,2048); # reducing this one allows one to increase the FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH,2048);  # doesn't work for this one
#cap.set(cv2.CAP_PROP_XI_DOWNSAMPLING,0)
#print cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#print cap.get(cv2.CAP_PROP_FRAME_HEIGHT); 


cap.set(cv2.CAP_PROP_EXPOSURE,3000)
cap.set(cv2.CAP_PROP_GAIN,1)
ret, frame = cap.read()

### initialising the histogram
if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==0 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==5:
  x=np.arange(0,256,4)
if cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==1 or cap.get(cv2.CAP_PROP_XI_DATA_FORMAT)==6:
  x=np.arange(0,1024,4)
hist=np.ones(np.shape(x))

#initialising graph and axes
rat = 0.7
Width=7
Height=7.
fig=plt.figure(figsize=(Height, Width))
axim = fig.add_axes([0.15, 0.135, rat, rat*(Height/Width)])
cax = fig.add_axes([0.17+rat, 0.15, 0.02, rat*(Height/Width)])
axc = fig.add_axes([0.17+rat, 0.15, 0.07, rat*(Height/Width)])
axhist=fig.add_axes([0.15,(0.17+rat),rat,0.1])
axhist.set_xlim([0,max(x)])
axhist.set_ylim([0,1])

im = axim.imshow(frame,cmap=plt.cm.gray,interpolation='nearest')
li,= axhist.plot(x,hist)
cb = fig.colorbar(im, cax=cax)
cax.axis('off')
axc.axis('off')

### define axis here
axcolor = 'lightgoldenrodyellow'
axExp = plt.axes([0.15, 0.02,rat, 0.03], axisbg=axcolor)
sExp = Slider(axExp, 'Exposure', 200, 50000, valinit=3000) #Exposition max = 1000000
axGain= plt.axes([0.15, 0.07,rat, 0.03], axisbg=axcolor)
sGain = Slider(axGain, 'Gain', -1, 6, valinit=1)

def update(val):
  cap.set(cv2.CAP_PROP_EXPOSURE,sExp.val)
  cap.set(cv2.CAP_PROP_GAIN,sGain.val)
  fig.canvas.draw_idle()
sExp.on_changed(update)
sGain.on_changed(update)



### define buttons here
RECax = plt.axes([0.01, (0.15+rat)/2, 0.05, 0.05])
button = Button(RECax, 'REC', color='red', hovercolor='0.975')
def REC(event):
  t0=time.time()
  i=0
  while(i<1200):
    ret, frame = cap.read()
    image=sitk.GetImageFromArray(frame)
    sitk.WriteImage(image,"/home/corentin/Bureau/ximea/"+"img_%.5d.tiff" %i) ### works fast in 8 or 16 bit, always use sitk.
    i+=1
  t=time.time()-t0
  print t
button.on_clicked(REC)


### Main
def get_frame(i):
  ret, frame = cap.read()
  if i == 1:
    cax.axis('on')
  im.set_data(frame)
  im.set_clim([frame.min(), frame.max()])
  histogram=cv2.calcHist([frame],[0],None,[len(x)],[0,max(x)])
  li.set_ydata((histogram-histogram.min())/(histogram.max()-histogram.min()))
  return cax, axim , axc, axhist



ani = animation.FuncAnimation(fig, get_frame, interval=20, frames=20, blit=False)
plt.show()
    
    
    
  #except KeyboardInterrupt:
    #break
    #plt.close()
    #cap.release()
  

  
##### This part is used to save a sample of image.
##frame={}
##i=0
##std_=3.0
##t0=time.time()
##while(i<2000):
  #####ret, frame[i] = cap.read()
  ##ret, frame = cap.read()
  ##image=sitk.GetImageFromArray(frame)
  ##sitk.WriteImage(image,"/home/corentin/Bureau/ximea/"+"img_.tiff") ### works fast in 8 or 16 bit, always use sitk.
  ##i+=1
##t=time.time()-t0

##print "t=%s" %t


#plt.hist(frame.ravel(),256,[0,1024]);
#plt.show()

#hist_full = cv2.calcHist([frame],[0],None,[256],[0,1024]) # 
#plt.plot(hist_full)
#plt.xlim([0,256])

#plt.show()