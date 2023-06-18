# -*- coding: utf-8 -*-
"""predict.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HM_nr0THP6XsZ6Oq2YYQcfC5qSTWPZYp
"""

import cv2 as cv
from skimage.feature import graycomatrix, graycoprops
import joblib
import warnings
from keras.models import load_model 
from torchvision import transforms
import torch

width, height = 70, 100
distance = 10
teta = 90
features=[]

#feature extraction function

def GLCM(imagepath):
  image=open(imagepath)
  glcm = graycomatrix(image , [distance], [teta], levels=256, symmetric=True, normed=True)
  contrast = graycoprops(glcm, 'contrast')[0][0]
  correlation = graycoprops(glcm, 'correlation')[0][0]
  energy = graycoprops(glcm, 'energy')[0][0]
  homogeneity = graycoprops(glcm, 'homogeneity')[0][0]
  features.append([contrast, correlation, energy, homogeneity]) 
  return features

#preprocesing function

def preprocessingImage(imagepath):
    image=image.open(imagepath)
    test_transforms=transforms.Compose([transforms.Resize(255),transforms.ToTensor()])
    test_img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    test_img_gray = cv.cvtColor(test_img, cv.COLOR_RGB2GRAY)
    test_img_thresh = cv.adaptiveThreshold(test_img_gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,11,3)
    cnts = cv.findContours(test_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)
    for c in cnts:
        x,y,w,h = cv.boundingRect(c)
        test_img_ROI = test_img[y:y+h, x:x+w]
        break
    test_img_ROI_resize_gray = cv.cvtColor(test_img_ROI, cv.COLOR_RGB2GRAY)
    imageTensor=test_transforms(test_img_ROI_resize_gray)
    return imageTensor

def predictImage (imagepath,verbose = False):
  if not verbose:
    warnings.filterwarnings('ignore')
  model_Path= '/model path from the folder models which contains ML model with pkl extention' 
  try:
    check_if_model_is_loaded = type(model)
  except:
    model=load_model(model_Path)
  model.eval() #parse model to script
  if verbose:
    print('Model Loaded Successfully!')
  InputImage=preprocessingImage(imagepath)
  TestedInputImage=TestedInputImage[None,:,:,:]
  ps=torch.exp(model(TestedInputImage))
  topconf,topclass = ps.topk(1,dim=1)
  if topclass.item == 1 :
    return {'class' : 'Normal' , 'confidence': str(topconf.item())}
  else :  
    return {'class' : 'AbNormal' , 'confidence': str(topconf.item())}