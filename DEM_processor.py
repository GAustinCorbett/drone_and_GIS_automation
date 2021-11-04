# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 10:50:50 2021

@author: gaust
"""
from osgeo import gdal
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog


def Zmeterstofeet(rootfp, infile):
    
    outfile = infile + "_Zft"
    in_fp = os.path.join(rootfp, infile + ".tif")
    out_fp = os.path.join(rootfp, outfile + ".tif")
    
    # International ft per meter conversion factor
    conv = 3.2808398950131 
    
    #The actual gdal raster object
    ds = gdal.Open(in_fp)
    
    #Get transform/projection from input file to be used later in output
    transform = ds.GetGeoTransform()
    proj = ds.GetProjection()
    
    #Pull the data values out of the gdal raster object
    band = ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    array = band.ReadAsArray()
    
    #Strip out -9999 nodata values so it doesn't get multiplied by conv. factor
    array_masked = np.ma.masked_values(array, nodata)
    
    #Apply conversion factor
    array_ft = array_masked*conv
    
    

    #Create a new output dataset to put the data from array_ft
    
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    outds = driver.Create(out_fp,
                          xsize = array_ft.shape[1],
                          ysize = array_ft.shape[0],
                          bands = 1,
                          eType = gdal.GDT_Float32)
    
    # Apply geolocation stuff to output dataset  
    outds.SetGeoTransform(transform)
    outds.SetProjection(proj)
    
    #Actually add the data into the output dataset by adding a band and writing data to band
    outband = outds.GetRasterBand(1)
    outband.WriteArray(array_ft)
    outband.SetNoDataValue(-9999)
    outband.FlushCache()
    
    #Necessary to avoid weird bug where output holds no actual data:
    outband = None
    outds = None
    
    return(outfile)

def get_resolution(rootfp, in_file, num_cells):
    # numcells = The roughly desired number of columns (or rows) if the raster were sqare  
    
    in_fp = os.path.join(rootfp, in_file + ".tif")
    #Read in array so we can get the right resolution to average ~200x200 = 40,000 raster
    ds = gdal.Open(in_fp)
    band = ds.GetRasterBand(1)
    tf = ds.GetGeoTransform()
  
    src_res = tf[1] #source resolution
    array = band.ReadAsArray()
        
    #Calc average number of raster cells for legnth and width
    
    avg_cells = np.average(array.shape)
    
    #Average Total distance
    avg_dist = avg_cells * src_res
    
    trgt_res = avg_dist / num_cells
    return(trgt_res)
"""
def downsample(rootfp, in_file, res):
          
    in_fp = os.path.join(rootfp, in_file + ".tif")
    #out_fp = os.path.join(rootfp, in_file + "_ft_" + str(res)[0:3] + ".tif")
    
    outfile = in_file + f"_{res:.2f}"
    out_fp = os.path.join(rootfp, outfile + ".tif")
    gdal.Translate(out_fp,
                   in_fp,
                   xRes=res,
                   yRes=res,
                   resampleAlg="bilinear",
                   #resampleAlg="nearest",
                   format='GTiff')
    return (outfile)
"""


"""This follwoing stuff is in main() in order to limit scope of variables 
since I use the same names for variables in functions.
"""
def reproject(rootfp, infile, res, crs):
    
    in_fp = os.path.join(rootfp, infile + ".tif")
    
    crs_sani = crs.replace(":", "")
    outfile = infile + "_" + crs_sani + f"-{res:.2f}m"
        
    out_fp = os.path.join(rootfp, outfile + ".tif")
    ds = gdal.Open(in_fp)
    dsReprj = gdal.Warp(out_fp, ds, xRes = res, yRes=res, dstSRS=crs)
    
    return(outfile)
    
def main():
    
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    rootfp = os.path.dirname(file_path)
    infile = os.path.splitext(os.path.basename(file_path))[0]
    
    #rootfp = "C:/Users/gaust/Desktop/"
    #infile = "dtm"
    crs = "EPSG:3489"
    
    infile2 = Zmeterstofeet(rootfp, infile)
    
    
    res = get_resolution(rootfp, infile2, 200)
    
    #infile3 = downsample(rootfp, infile2, res)
       
    reproject(rootfp, infile2, res, crs)
    
    
    return

main()


"""
conv = 3.2808398950131
ds = gdal.Open("C:/Users/gaust/Desktop/dtm.tif")

transform = ds.GetGeoTransform()
proj = ds.GetProjection()

band = ds.GetRasterBand(1)
nodata = band.GetNoDataValue()
array = band.ReadAsArray()

array_masked = np.ma.masked_values(array, nodata)

array_ft = array_masked*conv

plt.figure()
#plt.imshow(array_filter_nodata)
plt.imshow(array_ft)

driver = gdal.GetDriverByName("GTiff")
driver.Register()

outfp = "C:/Users/gaust/Desktop/dtm_ft.tif"
outds = driver.Create(outfp,
                      xsize = array_ft.shape[1],
                      ysize = array_ft.shape[0],
                      bands = 1,
                      eType = gdal.GDT_Float32)
outds.SetGeoTransform(transform)
outds.SetProjection(proj)
outband = outds.GetRasterBand(1)
outband.WriteArray(array_ft)
outband.SetNoDataValue(-9999)
outband.FlushCache()

outband = None
outds = None
"""
