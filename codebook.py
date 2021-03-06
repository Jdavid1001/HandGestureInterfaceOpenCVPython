# -*- coding: utf-8 -*-
#Special Shout out to
#http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.148.9778&rep=rep1&type=pdf
#For code samples and my template
#Also, shout out to 'Learning OpenCV' by Bradski and Kaehler for their explanations
#Since we are allowed to use others' work for this class, I changed it so I could
#understand it now and in the future

import numpy as np

alpha = 5
beta = 0.95

Tdel = 80
Tadd = 140
Th= 80

#Index of value
minVal,maxVal,freq,l,p,q = 0,1,2,3,4,5

class CodeBook():
    def __init__(self,height,width):
        self.height = height
        self.width = width
        self.M = np.empty((height, width), dtype=np.object)
        self.H = np.empty((height, width), dtype=np.object)
        self.time = 1
        
        fillerFunc = np.frompyfunc(lambda x: list(), 1, 1) #Use frompyfunc for speed
        fillerFunc(self.M,self.M)
        fillerFunc(self.H,self.H)

    def updatev(self,gray,cb):
        I,t = gray,self.time     
        if not cb:
            c = [max(0.0,I-alpha),min(255.0,I+alpha),1,t-1,t,t]
            cb.append(c)
        else:
            found = False
            for cm in cb:
                if(cm[minVal]<=I<=cm[maxVal] and not found): #part of background
                    cm[minVal] = ((I-alpha)+(cm[freq]*cm[minVal]))/(cm[freq]+1.0)  #subtract by ever decreasing vals  
                    cm[maxVal] = ((I+alpha)+(cm[freq]*cm[maxVal]))/(cm[freq]+1.0)  #add onto by decreasing vals
                    cm[freq] += 1
                    cm[l] = 0
                    cm[q] = t
                    found = True
                else:
                    cm[l] = max(cm[l],10-cm[q]+cm[p]-1)
            if not found:
                c = [max(0.0,I-alpha),min(255.0,I+alpha),1,t-1,t,t]
                cb.append(c)                
        return cb
    def update(self,gray):       
        M = self.M
        updatev = np.vectorize(self.updatev,otypes=[np.object])
        self.M=updatev(gray,M)
        self.time += 1   
    def foregroundVector(self,gray,cwm,cwh): #part of background
        I,t = gray,self.time
        found = False
        for cm in cwm:
            if(cm[minVal]<=I<=cm[maxVal] and not found):
                cm[minVal] = (1-beta)*(I-alpha) + (beta*cm[minVal])
                cm[maxVal] = (1-beta)*(I+alpha) + (beta*cm[maxVal])
                cm[freq] += 1
                cm[l] = 0
                cm[q] = t
                found = True
            else:
                cm[l] += 1
        cwm[:] = [cw for cw in cwm if cw[l]<Tdel]  
        if found: return 0
        for cm in cwh:
            if(cm[minVal]<=I<=cm[maxVal] and not found):
                cm[minVal] = (1-beta)*(I-alpha) + (beta*cm[minVal])
                cm[maxVal] = (1-beta)*(I+alpha) + (beta*cm[maxVal])
                cm[freq] += 1
                cm[l] = 0
                cm[q] = t
                found = True
            else:
                cm[l] += 1
        if not found:
            c = [max(0.0,I-alpha),min(255.0,I+alpha),1,0,t,t]
            cwh.append(c)
        cwh[:] = [cw for cw in cwh if cw[l]<Th]
        tomove = [cw for cw in cwh if cw[freq]>Tadd]
        cwh[:] = [cw for cw in cwh if not cw in tomove]
        cwm.extend(tomove)
        return 255
    def foreground(self,gray):  
        M,H = self.M,self.H
        fgvFunc = np.vectorize(self.foregroundVector,otypes=[np.uint8])
        foreground = fgvFunc(gray,M,H)
        self.time += 1
        return foreground
