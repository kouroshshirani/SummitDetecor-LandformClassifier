#  -*- coding: utf-8 -*-
import time
import sys
import numpy
import random
import math
import shapefile
from PIL import Image
import tifffile
            
try:
    import Tkinter as tk
    # ------------------------------------
    from Tkinter import *
    from tkFileDialog import askdirectory
    from tkFileDialog import askopenfilename
    # ------------------------------------
except ImportError:
    import tkinter as tk
try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True
import Landform_Classifier_support
def vp_start_gui():
    global val, w, root
    root = tk.Tk()
    Ridge_and_Summit_Recognizer_plus_Landform_Classifier_support.set_Tk_var()
    top = Toplevel1 (root)
    Ridge_and_Summit_Recognizer_plus_Landform_Classifier_support.init(root, top)
    root.mainloop()
w = None
def create_Toplevel1(root, *args, **kwargs):
    global w, w_win, rt
    rt = root
    w = tk.Toplevel (root)
    Ridge_and_Summit_Recognizer_plus_Landform_Classifier_support.set_Tk_var()
    top = Toplevel1 (w)
    Ridge_and_Summit_Recognizer_plus_Landform_Classifier_support.init(w, top, *args, **kwargs)
    return (w, top)
def destroy_Toplevel1():
    global w
    w.destroy()
    w = None
# --------------------------------------------------------------------
def destroy_window():
    global root
    root.destroy()
# -------------------------------------------------------------------- 
class Toplevel1:
    def __init__(self, top=None):
        global OutputrasterPathFile
        OutputrasterPathFile = ''
        # --------------------------------------------------------------------
        def get_out_raster_path():
            path = askdirectory()
            Output_raster_Path_File.set(path)
            OutputrasterPathFile = path
        def get_out_Vector_path():
            path = askdirectory()
            Output_vector_Path_File.set(path)    
        def get_inputRaster_path():
            from PIL import Image
            #path = askdirectory()
            file_path = askopenfilename()
            pathInputRaster.set(file_path)
            if file_path.endswith('.tif'):
                tiff_raster = Image.open(file_path)
                tiff_array = numpy.array(tiff_raster)
                minValue = numpy.min(tiff_array)
                maxValue = numpy.max(tiff_array)
                minElevs.set(str(minValue))
                maxElevs.set(str(maxValue))  
            if file_path.endswith('.asc') or file_path.endswith('.txt'):
                matrix = numpy.loadtxt(file_path,skiprows = 6)
                minValue = numpy.min(matrix)
                maxValue = numpy.max(matrix)
                minElevs.set(str(minValue))
                maxElevs.set(str(maxValue))
        def show_MovingWindow():
            #print Algorithm_Number.get()
            try: 
                rows = int(float(rowDimension.get()))
                columns = int(float(columnDimension.get()))
                if rows != columns:
                    colors = 'red'
                if (rows == columns) and (rows%2 != 0) and (columns%2 != 0):
                    colors = 'green'
                win = Tk()
                win.title("Moving Window")
                def printer(r,c):
                    Button(win,text = str(r)+','+str(c), width = 6, height = 2,bg = colors).grid(row =r,column = c)
                for r in range(rows):
                    for c in range(columns):
                        B = Button(win,text = str(r)+','+str(c), width = 6, height =2,
                                   command = lambda r=r, c=c: printer(r,c)).grid(row = r,column = c)
                win.mainloop()
            except:
                win = Tk()
                win.geometry('400x100')
                win.title("Error: Moving Window")
                Label(win,text = 'Warning: Row or Column size is Blank',font = 12,fg = 'red').place(relx=0.083, rely=0.235, height=30, width=300)
                win.mainloop()
        # ---------------------------------------------
        # ---------------------------------------------
        def MainRun():
            global Dim
            Dimensions = rowDimension.get()
            Dimensions = int(Dimensions)
            path_Input_File = pathInputRaster.get()
            path_Out_File = Output_raster_Path_File.get()  
            Output_Vector_File_Path = Output_vector_Path_File.get()
            Vectorization_Tresholds = float(Threshold_algorithm.get())
            Elevation_Tresholds = float(Elevation_Threshold.get())
            Algorithm = Algorithm_Number.get()
            Algorithm = int(Algorithm)
            # Main Body Code
            def indexGenerator(winsize):
                windowIndexList = []
                for i in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                    for j in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                        windowIndexList.append([i,j])
                return windowIndexList
            def headerOrganizer(winsize,inPutRaster,outputRaster):
                listHeader = []
                n = 0
                for lines in inPutRaster:
                    n+=1
                    if n<7:
                        linelist = lines.split(' ')
                        linelist[-1] = linelist[-1].strip()
                        listHeader.append([linelist[0],float(linelist[-1])])
                n =-1
                for items in listHeader:
                    n+=1
                    if n == 0 or n == 1:
                        items[1] = items[1]-(winsize-1)
                    if n == 2:
                        items[1] = items[1]+(((winsize-1)/2)*listHeader[4][1])
                    if n == 3:
                        items[1] = items[1]+(((winsize-1)/2)*listHeader[4][1])
                    outputRaster.write(items[0]+' '*(14-len(items[0]))+ str(items[1])+'\n')    
            def headerOrganizer_tiff(winsizes,outputRaster):
                with tifffile.TiffFile(path_Input_File) as tif:
                    tif_tags = {}
                    for tag in tif.pages[0].tags.values():
                        name, value = tag.name, tag.value
                        tif_tags[name] = value
                    image = tif.pages[0].asarray()
                    tif_tags =tif_tags.items()
                    x_ULC = float(tif_tags[10][1][3])
                    y_ULC = float(tif_tags[10][1][4])
                    x_LLC = x_ULC
                    columns =  int(tif_tags[13][1])
                    rows =  int(tif_tags[4][1])
                    XcellSize = float(tif_tags[19][1][0])
                    YCellSize = float(tif_tags[19][1][1])
                    y_LLC = y_ULC - (YCellSize * rows)
                    outputRaster.write('ncols         '+str(columns - (winsizes-1))+'\n')
                    outputRaster.write('nrows         '+str(rows - (winsizes-1))+'\n')
                    outputRaster.write('xllcorner     '+str(x_LLC + (((winsizes-1)/2.0)*XcellSize)-(XcellSize/2.0))+'\n')
                    outputRaster.write('yllcorner     '+str(y_LLC + (((winsizes-1)/2.0)*YCellSize) + (YCellSize/2.0))+'\n')
                    outputRaster.write('cellsize      '+str(XcellSize)+'\n')
                    outputRaster.write('NODATA_value  '+str(-9999)+'\n')    
            def CPRS(winsizes,DEM,inPutRaster,outputRaster):
                start_time = time.time()
                global AN
                if path_Input_File.endswith('.tif'):
                        with tifffile.TiffFile(path_Input_File) as tif:
                            tif_tags = {}
                            for tag in tif.pages[0].tags.values():
                                name, value = tag.name, tag.value
                                tif_tags[name] = value
                            image = tif.pages[0].asarray()
                            tif_tags =tif_tags.items()
                            x_ULC = float(tif_tags[10][1][3])
                            y_ULC = float(tif_tags[10][1][4])
                            x_LLC = x_ULC
                            columns =  int(tif_tags[13][1])
                            rows =  int(tif_tags[4][1])
                            XcellSize = float(tif_tags[19][1][0])
                            YCellSize = float(tif_tags[19][1][1])
                        y_LLC = y_ULC - (YCellSize * rows)
                        headerOrganizer_tiff(winsizes,outputRaster)
                if path_Input_File.endswith('.asc') or path_Input_File.endswith('.txt'):
                    rasterIn = open(path_Input_File,'r')
                    headers = []
                    n = 0
                    for i in rasterIn:
                        n+=1
                        if n<=6:
                            Line = i.split(' ')
                            Line[-1] = Line[-1].strip()
                            headers.append([Line[0],Line[-1]])
                    x_LLC = float(headers[2][1])
                    y_LLC = float(headers[3][1])
                    XcellSize = float(headers[4][1])
                    YCellSize = float(headers[4][1])
                    headerOrganizer(winsizes,inPutRaster,outputRaster)
                algorithmsname = ['SMRS','CMRS','CPRS','TPI']
                w = shapefile.Writer(Output_Vector_File_Path + '\\'+algorithmsname[Algorithm-1]+'_winSize_'+str(Dimensions)+'_VectorizationTresholds_'+str(Vectorization_Tresholds)+'_ElevationTresholds'+str(Elevation_Tresholds), shapeType=shapefile.POINT)  
                w.field('x-Coordinate', 'C')
                w.field('y-Coordinate', 'C')
                w.field('z-Coordinate', 'C')
                w.field('Threshold', 'C')
                #headerOrganizer(winsizes,inPutRaster,outputRaster)
                rows = DEM.shape[0]
                columns = DEM.shape[1]
                winIndex = indexGenerator(winsizes)
                r_code = ((winsizes-1)/2)-1
                yCoordinate = (YCellSize/2.0)+((y_LLC+(rows*YCellSize)) - (((winsizes-1)/2)*YCellSize))
                for r in range(rows-(winsizes-1)):
                    yCoordinate-= YCellSize
                    xCoordinate = (x_LLC + (((winsizes-1)/2)*XcellSize))-(XcellSize / 2.0)
                    print (r_code,' From:',rows-(winsizes-1))
                    ProgressBar(r_code,rows-(winsizes-1))
                    r_code += 1
                    c_code = ((winsizes-1)/2)-1
                    for c in range(columns-(winsizes-1)):
                        xCoordinate += XcellSize
                        c_code +=1
                        winValue = []
                        for pixels in winIndex:
                            winValue.append(DEM[r_code+pixels[0],c_code+pixels[1]])
                        # CPRS Algorithm
                        if DEM[r_code,c_code] != -9999.0:
                            counter = 0.0
                            for i in winValue:
                                if i != DEM[r_code,c_code]:
                                    if DEM[r_code,c_code] > i:
                                        counter +=1
                            CPRSValue = (counter/((winsizes*winsizes)-1))*100.0
                        else:
                            CPRSValue = -9999.0
                        outputRaster.write(str(CPRSValue)+' ')
                        if DEM[r_code,c_code] >= Elevation_Tresholds:
                            if CPRSValue >= float(Vectorization_Tresholds):
                                w.point(xCoordinate,yCoordinate)
                                w.record(str(xCoordinate),str(yCoordinate),str(DEM[r_code,c_code]),str(CPRSValue))
                    outputRaster.write('\n')
                AN = algorithmsname[Algorithm-1]
                ProgressBar(rows-(winsizes-1),rows-(winsizes-1))
                end_time = time.time()
                runtime_duration = end_time - start_time
                print ('Time Duration : ',runtime_duration)
                return AN
            def SMRS(winsize,DEM,inPutRaster,outputRaster):
                start_time = time.time()
                global AN
                if path_Input_File.endswith('.tif'):
                    with tifffile.TiffFile(path_Input_File) as tif:
                        tif_tags = {}
                        for tag in tif.pages[0].tags.values():
                            name, value = tag.name, tag.value
                            tif_tags[name] = value
                        image = tif.pages[0].asarray()
                        tif_tags =tif_tags.items()
                        x_ULC = float(tif_tags[10][1][3])
                        y_ULC = float(tif_tags[10][1][4])
                        x_LLC = x_ULC
                        columns =  int(tif_tags[13][1])
                        rows =  int(tif_tags[4][1])
                        XcellSize = float(tif_tags[19][1][0])
                        YCellSize = float(tif_tags[19][1][1])
                        y_LLC = y_ULC - (YCellSize * rows)
                        headerOrganizer_tiff(winsize,outputRaster)
                if path_Input_File.endswith('.asc') or path_Input_File.endswith('.txt'):
                    rasterIn = open(path_Input_File,'r')
                    headers = []
                    n = 0
                    for i in rasterIn:
                        n+=1
                        if n<=6:
                            Line = i.split(' ')
                            Line[-1] = Line[-1].strip()
                            headers.append([Line[0],Line[-1]])
                    x_LLC = float(headers[2][1])
                    y_LLC = float(headers[3][1])
                    XcellSize = float(headers[4][1])
                    YCellSize = float(headers[4][1])
                    headerOrganizer(winsize,inPutRaster,outputRaster)
                algorithmsname = ['SMRS','CMRS','CPRS','TPI']
                w = shapefile.Writer(Output_Vector_File_Path + '\\'+algorithmsname[Algorithm-1]+'_winSize_'+str(Dimensions)+'_VectorizationTresholds_'+str(Vectorization_Tresholds)+'_ElevationTresholds'+str(Elevation_Tresholds), shapeType=shapefile.POINT)  
                w.field('x-Coordinate', 'C')
                w.field('y-Coordinate', 'C')
                w.field('z-Coordinate', 'C')
                w.field('Threshold', 'C')    
                #headerOrganizer(winsize,inPutRaster,outputRaster)
                rows = DEM.shape[0]
                columns = DEM.shape[1]
                bigWindow = []
                for winsize in range(3,winsize+2,2):
                    windowIndexList = []
                    for i in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                        for j in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                            windowIndexList.append([i,j])
                    bigWindow.append(windowIndexList)
                bigWindow_new = []
                for Levels in range(1,len(bigWindow)):
                    Levels = Levels*-1
                    listNew = []
                    for i in bigWindow[Levels]:
                        if i not in bigWindow[Levels-1]:
                            listNew.append(i)
                    bigWindow_new.append(listNew)
                bigWindow_new.append([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]])
                bigWindow_new.append([[0,0]])
                rows = DEM.shape[0]
                columns = DEM.shape[1]    
                r_code = ((winsize-1)/2)-1
                yCoordinate = (YCellSize/2.0)+((y_LLC+(rows*YCellSize)) - (((winsize-1)/2)*YCellSize))
                for r in range(rows-(winsize-1)):
                    yCoordinate-= YCellSize
                    xCoordinate = (x_LLC + (((winsize-1)/2)*XcellSize))-(XcellSize / 2.0)
                    print (r_code,' From:',rows-(winsize-1))
                    ProgressBar(r_code,rows-(winsize-1))
                    r_code += 1
                    c_code = ((winsize-1)/2)-1
                    for c in range(columns-(winsize-1)):
                        xCoordinate += XcellSize
                        c_code +=1
                        winLevels = []
                        for levels in bigWindow_new:
                            listVAluesLevel = []
                            for items in levels:
                                Values = DEM[r_code + items[0],c_code +items[1]]
                                listVAluesLevel.append(Values)
                            winLevels.append(listVAluesLevel)
                        # Algorithm SMRS
                        if DEM[r_code,c_code] != -9999.0:
                            listMeans = []
                            for levels in winLevels:
                                meanLevels = sum(levels) / len(levels)
                                listMeans.append(meanLevels)
                            counter = 0.0
                            UnCounter = 0.0
                            for levels in range(len(listMeans)-1):
                                if listMeans[levels] < listMeans[levels+1]:
                                    counter+=1.0
                                else:
                                    UnCounter +=1.0
                            SMRS_Value = (counter / (counter+UnCounter))*100.0
                        else:
                            SMRS_Value = -9999.0

                        outputRaster.write(str(SMRS_Value)+' ')
                        if DEM[r_code,c_code] >= Elevation_Tresholds:
                            if SMRS_Value >= float(Vectorization_Tresholds):
                                w.point(xCoordinate,yCoordinate)
                                w.record(str(xCoordinate),str(yCoordinate),str(DEM[r_code,c_code]),str(SMRS_Value))
                    outputRaster.write('\n')
                AN = algorithmsname[Algorithm-1]
                ProgressBar(rows-(winsize-1),rows-(winsize-1))
                end_time = time.time()
                runtime_duration = end_time - start_time
                print ('Time Duration : ',runtime_duration)
                return AN
            def CMRS(winsize,DEM,inPutRaster,outputRaster):
                start_time = time.time()
                global AN
                if path_Input_File.endswith('.tif'):
                    with tifffile.TiffFile(path_Input_File) as tif:
                        tif_tags = {}
                        for tag in tif.pages[0].tags.values():
                            name, value = tag.name, tag.value
                            tif_tags[name] = value
                        image = tif.pages[0].asarray()
                        tif_tags =tif_tags.items()
                        x_ULC = float(tif_tags[10][1][3])
                        y_ULC = float(tif_tags[10][1][4])
                        x_LLC = x_ULC
                        columns =  int(tif_tags[13][1])
                        rows =  int(tif_tags[4][1])
                        XcellSize = float(tif_tags[19][1][0])
                        YCellSize = float(tif_tags[19][1][1])
                        y_LLC = y_ULC - (YCellSize * rows)
                        headerOrganizer_tiff(winsize,outputRaster)
                if path_Input_File.endswith('.asc') or path_Input_File.endswith('.txt'):
                    rasterIn = open(path_Input_File,'r')
                    headers = []
                    n = 0
                    for i in rasterIn:
                        n+=1
                        if n<=6:
                            Line = i.split(' ')
                            Line[-1] = Line[-1].strip()
                            headers.append([Line[0],Line[-1]])
                    x_LLC = float(headers[2][1])
                    y_LLC = float(headers[3][1])
                    XcellSize = float(headers[4][1])
                    YCellSize = float(headers[4][1])
                    headerOrganizer(winsize,inPutRaster,outputRaster)
                algorithmsname = ['SMRS','CMRS','CPRS','TPI']
                w = shapefile.Writer(Output_Vector_File_Path + '\\'+algorithmsname[Algorithm-1]+'_winSize_'+str(Dimensions)+'_VectorizationTresholds_'+str(Vectorization_Tresholds)+'_ElevationTresholds'+str(Elevation_Tresholds), shapeType=shapefile.POINT)
                w.field('x-Coordinate', 'C')
                w.field('y-Coordinate', 'C')
                w.field('z-Coordinate', 'C')
                w.field('Threshold', 'C') 
                #headerOrganizer(winsize,inPutRaster,outputRaster)
                rows = DEM.shape[0]
                columns = DEM.shape[1]
                bigWindow = []
                for winsize in range(3,winsize+2,2):
                    windowIndexList = []
                    for i in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                        for j in range(-1 *((winsize-1)/2),((winsize-1)/2)+1):
                            windowIndexList.append([i,j])
                    bigWindow.append(windowIndexList)
                bigWindow_new = []
                for Levels in range(1,len(bigWindow)):
                    Levels = Levels*-1
                    listNew = []
                    for i in bigWindow[Levels]:
                        if i not in bigWindow[Levels-1]:
                            listNew.append(i)
                    bigWindow_new.append(listNew)
                bigWindow_new.append([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]])
                bigWindow_new.append([[0,0]])
                rows = DEM.shape[0]
                columns = DEM.shape[1]    
                r_code = ((winsize-1)/2)-1
                yCoordinate = (YCellSize/2.0)+((y_LLC+(rows*YCellSize)) - (((winsize-1)/2)*YCellSize))
                for r in range(rows-(winsize-1)):
                    yCoordinate-= YCellSize
                    xCoordinate = (x_LLC + (((winsize-1)/2)*XcellSize))-(XcellSize / 2.0)
                    print (r_code, ' From:', rows - (winsize - 1))
                    ProgressBar(r_code,rows-(winsize-1))
                    r_code += 1
                    c_code = ((winsize-1)/2)-1
                    for c in range(columns-(winsize-1)):
                        xCoordinate += XcellSize
                        c_code +=1
                        winLevels = []
                        for levels in bigWindow_new:
                            listVAluesLevel = []
                            for items in levels:
                                Values = DEM[r_code + items[0],c_code +items[1]]
                                listVAluesLevel.append(Values)
                            winLevels.append(listVAluesLevel)
                        # CMRS Algorithm
                        if DEM[r_code,c_code] != -9999.0:
                            Counter = 0.0
                            UnCounter = 0.0
                            for items in range(len(winLevels)-1):
                                for i in winLevels[items]:
                                    for j in winLevels[items+1]:
                                        if i<j:
                                            Counter +=1
                                        else:
                                            UnCounter+=1
                            meanCMRS = (Counter / (Counter + UnCounter))*100.0
                        else:
                            meanCMRS = -9999.0
                        outputRaster.write(str(meanCMRS)+' ')
                        if DEM[r_code,c_code] >= Elevation_Tresholds:
                            if meanCMRS >= float(Vectorization_Tresholds):
                                w.point(xCoordinate,yCoordinate)
                                w.record(str(xCoordinate),str(yCoordinate),str(DEM[r_code,c_code]),str(meanCMRS))
                    outputRaster.write('\n')
                AN = algorithmsname[Algorithm-1]
                ProgressBar(rows-(winsize-1),rows-(winsize-1))
                end_time = time.time()
                runtime_duration = end_time - start_time
                print ('Time Duration : ',runtime_duration)
                return AN

            def TPI(winsizes,DEM,inPutRaster,outputRaster):
                start_time = time.time()
                global AN
                if path_Input_File.endswith('.tif'):
                        with tifffile.TiffFile(path_Input_File) as tif:
                            tif_tags = {}
                            for tag in tif.pages[0].tags.values():
                                name, value = tag.name, tag.value
                                tif_tags[name] = value
                            image = tif.pages[0].asarray()
                            tif_tags =tif_tags.items()
                            x_ULC = float(tif_tags[10][1][3])
                            y_ULC = float(tif_tags[10][1][4])
                            x_LLC = x_ULC
                            columns =  int(tif_tags[13][1])
                            rows =  int(tif_tags[4][1])
                            XcellSize = float(tif_tags[19][1][0])
                            YCellSize = float(tif_tags[19][1][1])
                        y_LLC = y_ULC - (YCellSize * rows)
                        headerOrganizer_tiff(winsizes,outputRaster)
                if path_Input_File.endswith('.asc') or path_Input_File.endswith('.txt'):
                    rasterIn = open(path_Input_File,'r')
                    headers = []
                    n = 0
                    for i in rasterIn:
                        n+=1
                        if n<=6:
                            Line = i.split(' ')
                            Line[-1] = Line[-1].strip()
                            headers.append([Line[0],Line[-1]])
                    x_LLC = float(headers[2][1])
                    y_LLC = float(headers[3][1])
                    XcellSize = float(headers[4][1])
                    YCellSize = float(headers[4][1])
                    headerOrganizer(winsizes,inPutRaster,outputRaster)
                algorithmsname = ['SMRS','CMRS','CPRS','TPI']
                w = shapefile.Writer(Output_Vector_File_Path + '\\'+algorithmsname[Algorithm-1]+'_winSize_'+str(Dimensions)+'_VectorizationTresholds_'+str(Vectorization_Tresholds)+'_ElevationTresholds'+str(Elevation_Tresholds), shapeType=shapefile.POINT)
                w.field('x-Coordinate', 'C')
                w.field('y-Coordinate', 'C')
                w.field('z-Coordinate', 'C')
                w.field('Threshold', 'C')
                #headerOrganizer(winsizes,inPutRaster,outputRaster)
                rows = DEM.shape[0]
                columns = DEM.shape[1]
                winIndex = indexGenerator(winsizes)
                r_code = ((winsizes-1)/2)-1
                yCoordinate = (YCellSize/2.0)+((y_LLC+(rows*YCellSize)) - (((winsizes-1)/2)*YCellSize))
                TPI_Raster = []
                TPI_max = []
                TPI_min = []
                for r in range(rows-(winsizes-1)):
                    TPI_row = []
                    TPI_row_max = []
                    TPI_row_min = []
                    yCoordinate-= YCellSize
                    xCoordinate = (x_LLC + (((winsizes-1)/2)*XcellSize))-(XcellSize / 2.0)
                    print (r_code, ' From:', rows - (winsizes - 1))
                    ProgressBar(r_code,rows-(winsizes-1))
                    r_code += 1
                    c_code = ((winsizes-1)/2)-1
                    for c in range(columns-(winsizes-1)):
                        xCoordinate += XcellSize
                        c_code +=1
                        winValue = []
                        for pixels in winIndex:
                            winValue.append(DEM[r_code+pixels[0],c_code+pixels[1]])
                        # TPI Algorithm
                        if DEM[r_code,c_code] != -9999.0:
                            counter = 0.0
                            nCounter = 0
                            
                            for i in winValue:
                                if i != DEM[r_code,c_code]:
                                    counter +=i
                                    nCounter+=1
                            MAX_win = max(winValue)
                            MIN_win = min(winValue)
                            if nCounter != 0:
                                meanWin = counter / nCounter
                                TPIValue = DEM[r_code,c_code] - meanWin
                                TPI_row_max.append(TPIValue)
                                TPI_row_min.append(TPIValue)
                            else:
                                TPIValue = 0
                                TPI_row_max.append(TPIValue)
                                TPI_row_min.append(TPIValue)
                        else:
                            TPIValue = -9999.0
                        TPI_row.append(TPIValue)
                    #outputRaster.write('\n')
                    TPI_Raster.append(TPI_row)
                    TPI_max.append(max(TPI_row_max))
                    TPI_min.append(min(TPI_row_min))
                MAX = max(TPI_max)
                MIN = min(TPI_min)
                row_new = len(TPI_Raster)
                column_new = len(TPI_Raster[0])
                r_code = -1
                r_code_new = ((winsizes - 1) / 2) - 1
                c_code_new = ((winsizes - 1) / 2) - 1
                yCoordinate = (YCellSize/2.0)+((y_LLC+(rows*YCellSize)) - (((winsizes-1)/2)*YCellSize))
                for r in range(row_new):
                    yCoordinate-= YCellSize
                    xCoordinate = (x_LLC + (((winsizes-1)/2)*XcellSize))-(XcellSize / 2.0)
                    ProgressBar(r_code,row_new)
                    r_code += 1
                    r_code_new += 1
                    c_code_new = ((winsizes - 1) / 2) - 1
                    c_code = -1
                    for c in range(column_new):
                        xCoordinate += XcellSize
                        c_code +=1
                        c_code_new += 1
                        TPI_values = TPI_Raster[r_code][c_code]
                        TPI_values = 100.0 * ((TPI_values - MIN) /(MAX - MIN))
                        outputRaster.write(str(TPI_values) + ' ')
                        if DEM[r_code_new, c_code_new] >= Elevation_Tresholds:
                            if TPI_values >= float(Vectorization_Tresholds):
                                w.point(xCoordinate, yCoordinate)
                                w.record(str(xCoordinate), str(yCoordinate), str(DEM[r_code_new, c_code_new]), str(TPI_values))
                    outputRaster.write('\n')

                AN = algorithmsname[Algorithm-1]
                ProgressBar(rows-(winsizes-1),rows-(winsizes-1))
                end_time = time.time()
                runtime_duration = end_time - start_time
                print ('Time Duration : ',runtime_duration)
                return AN
            algorithmsname = ['SMRS','CMRS','CPRS','TPI']
            if Algorithm == 1:
                if path_Input_File.endswith('.tif'):
                    from PIL import Image
                    tiff_raster = Image.open(path_Input_File)
                    DEM = numpy.array(tiff_raster)
                    winsize = Dimensions
                    inPutRaster = DEM#open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')
                else:
                    DEM = numpy.loadtxt(path_Input_File,skiprows = 6)
                    winsize = Dimensions
                    inPutRaster = open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                        str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                        str(Dimensions) + '.asc','a+')
                SMRS(winsize,DEM,inPutRaster,outputRaster)
            if Algorithm == 2:
                if path_Input_File.endswith('.tif'):
                    from PIL import Image
                    tiff_raster = Image.open(path_Input_File)
                    DEM = numpy.array(tiff_raster)
                    winsize = Dimensions
                    inPutRaster = DEM#open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')
                else:
                    DEM = numpy.loadtxt(path_Input_File,skiprows = 6)
                    winsize = Dimensions
                    inPutRaster = open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                        str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                        str(Dimensions) + '.asc','a+')
                CMRS(winsize,DEM,inPutRaster,outputRaster)
            if Algorithm == 3:
                if path_Input_File.endswith('.tif'):
                    from PIL import Image
                    tiff_raster = Image.open(path_Input_File)
                    DEM = numpy.array(tiff_raster)
                    winsize = Dimensions
                    inPutRaster = inPutRaster = DEM#open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')                    
                else:
                    DEM = numpy.loadtxt(path_Input_File,skiprows = 6)
                    winsize = Dimensions
                    inPutRaster = open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')
                CPRS(winsize,DEM,inPutRaster,outputRaster)
            if Algorithm == 4:
                if path_Input_File.endswith('.tif'):
                    from PIL import Image
                    tiff_raster = Image.open(path_Input_File)
                    DEM = numpy.array(tiff_raster)
                    winsize = Dimensions
                    inPutRaster = DEM#open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')
                else:
                    DEM = numpy.loadtxt(path_Input_File,skiprows = 6)
                    winsize = Dimensions
                    inPutRaster = open(path_Input_File,'r')
                    outputRaster = open(path_Out_File + '\\'+'Ridgelines_'+
                                    str(algorithmsname[Algorithm-1])+'_WinSize_'+
                                    str(Dimensions) + '.asc','a+')
                TPI(winsize,DEM,inPutRaster,outputRaster)
            Dim = Dimensions
            return Dim
        # ---------------------------------------------
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])
        top.geometry("993x653+228+25")
        top.minsize(120, 1)
        top.maxsize(1370, 749)
        top.resizable(1, 1)
        top.title("Ridge and Summit Recognizer + Landform Classifier")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        self.Frame1 = tk.Frame(top)
        self.Frame1.place(relx=0.008, rely=0.014, relheight=0.237
                , relwidth=0.982)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(background="red")#0074e8
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="black")
        self.Label1 = tk.Label(self.Frame1)
        self.Label1.place(relx=0.021, rely=0.129, height=43, width=650)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="red")#0074e8
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font="-family {Segoe UI Black} -size 19 -weight bold")
        self.Label1.configure(foreground="#ffffff")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Ridge and Summit Recognizer + Landform Classifier''')
        self.Label1_2 = tk.Label(self.Frame1)
        self.Label1_2.place(relx=0.103, rely=0.774, height=23, width=230)
        self.Label1_2.configure(activebackground="#f9f9f9")
        self.Label1_2.configure(activeforeground="black")
        self.Label1_2.configure(background="red")#0074e8
        self.Label1_2.configure(disabledforeground="#a3a3a3")
        self.Label1_2.configure(font="-family {Segoe UI Black} -size 13 -weight bold")
        self.Label1_2.configure(foreground="#ffffff")
        self.Label1_2.configure(highlightbackground="#d9d9d9")
        self.Label1_2.configure(highlightcolor="black")
        self.Label1_2.configure(text='''''')
        self.Label1_3 = tk.Label(self.Frame1)
        self.Label1_3.place(relx=0.728, rely=0.645, height=23, width=230)
        self.Label1_3.configure(activebackground="#f9f9f9")
        self.Label1_3.configure(activeforeground="black")
        self.Label1_3.configure(background="red")#0074e8
        self.Label1_3.configure(disabledforeground="#a3a3a3")
        self.Label1_3.configure(font="-family {Segoe UI Black} -size 10 -weight bold")
        self.Label1_3.configure(foreground="#ffffff")
        self.Label1_3.configure(highlightbackground="#d9d9d9")
        self.Label1_3.configure(highlightcolor="black")
        self.Label1_3.configure(text='''Digital Terrain Modeling''')
        self.Frame2_5 = tk.Frame(self.Frame1)
        self.Frame2_5.place(relx=0.938, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_5.configure(relief='groove')
        self.Frame2_5.configure(borderwidth="2")
        self.Frame2_5.configure(relief="groove")
        self.Frame2_5.configure(background="#ffcab0")
        self.Frame2_5.configure(highlightbackground="#d9d9d9")
        self.Frame2_5.configure(highlightcolor="black")
        self.Frame2_6 = tk.Frame(self.Frame2_5)
        self.Frame2_6.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_6.configure(relief='groove')
        self.Frame2_6.configure(borderwidth="2")
        self.Frame2_6.configure(relief="groove")
        self.Frame2_6.configure(background="#ff8040")
        self.Frame2_6.configure(highlightbackground="#d9d9d9")
        self.Frame2_6.configure(highlightcolor="black")
        self.Frame2_7 = tk.Frame(self.Frame2_6)
        self.Frame2_7.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_7.configure(relief='groove')
        self.Frame2_7.configure(borderwidth="2")
        self.Frame2_7.configure(relief="groove")
        self.Frame2_7.configure(background="#ff8040")
        self.Frame2_7.configure(highlightbackground="#d9d9d9")
        self.Frame2_7.configure(highlightcolor="black")
        self.Frame2_1 = tk.Frame(self.Frame1)
        self.Frame2_1.place(relx=0.909, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_1.configure(relief='groove')
        self.Frame2_1.configure(borderwidth="2")
        self.Frame2_1.configure(relief="groove")
        self.Frame2_1.configure(background="#ffcab0")
        self.Frame2_1.configure(highlightbackground="#d9d9d9")
        self.Frame2_1.configure(highlightcolor="black")
        self.Frame2_2 = tk.Frame(self.Frame2_1)
        self.Frame2_2.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_2.configure(relief='groove')
        self.Frame2_2.configure(borderwidth="2")
        self.Frame2_2.configure(relief="groove")
        self.Frame2_2.configure(background="#ff8040")
        self.Frame2_2.configure(highlightbackground="#d9d9d9")
        self.Frame2_2.configure(highlightcolor="black")
        self.Frame2_3 = tk.Frame(self.Frame2_2)
        self.Frame2_3.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_3.configure(relief='groove')
        self.Frame2_3.configure(borderwidth="2")
        self.Frame2_3.configure(relief="groove")
        self.Frame2_3.configure(background="#ff8040")
        self.Frame2_3.configure(highlightbackground="#d9d9d9")
        self.Frame2_3.configure(highlightcolor="black")
        self.Frame2_4 = tk.Frame(self.Frame1)
        self.Frame2_4.place(relx=0.877, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_4.configure(relief='groove')
        self.Frame2_4.configure(borderwidth="2")
        self.Frame2_4.configure(relief="groove")
        self.Frame2_4.configure(background="#ffcab0")
        self.Frame2_4.configure(highlightbackground="#d9d9d9")
        self.Frame2_4.configure(highlightcolor="black")
        self.Frame2_2 = tk.Frame(self.Frame2_4)
        self.Frame2_2.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_2.configure(relief='groove')
        self.Frame2_2.configure(borderwidth="2")
        self.Frame2_2.configure(relief="groove")
        self.Frame2_2.configure(background="#ff8040")
        self.Frame2_2.configure(highlightbackground="#d9d9d9")
        self.Frame2_2.configure(highlightcolor="black")
        self.Frame2_8 = tk.Frame(self.Frame2_2)
        self.Frame2_8.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_8.configure(relief='groove')
        self.Frame2_8.configure(borderwidth="2")
        self.Frame2_8.configure(relief="groove")
        self.Frame2_8.configure(background="#ff8040")
        self.Frame2_8.configure(highlightbackground="#d9d9d9")
        self.Frame2_8.configure(highlightcolor="black")
        self.Frame2_3 = tk.Frame(self.Frame1)
        self.Frame2_3.place(relx=0.846, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_3.configure(relief='groove')
        self.Frame2_3.configure(borderwidth="2")
        self.Frame2_3.configure(relief="groove")
        self.Frame2_3.configure(background="#ffcab0")
        self.Frame2_3.configure(highlightbackground="#d9d9d9")
        self.Frame2_3.configure(highlightcolor="black")
        self.Frame2_4 = tk.Frame(self.Frame2_3)
        self.Frame2_4.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_4.configure(relief='groove')
        self.Frame2_4.configure(borderwidth="2")
        self.Frame2_4.configure(relief="groove")
        self.Frame2_4.configure(background="#ff8040")
        self.Frame2_4.configure(highlightbackground="#d9d9d9")
        self.Frame2_4.configure(highlightcolor="black")
        self.Frame2_9 = tk.Frame(self.Frame2_4)
        self.Frame2_9.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_9.configure(relief='groove')
        self.Frame2_9.configure(borderwidth="2")
        self.Frame2_9.configure(relief="groove")
        self.Frame2_9.configure(background="#ff8040")
        self.Frame2_9.configure(highlightbackground="#d9d9d9")
        self.Frame2_9.configure(highlightcolor="black")
        self.Frame2_5 = tk.Frame(self.Frame1)
        self.Frame2_5.place(relx=0.815, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_5.configure(relief='groove')
        self.Frame2_5.configure(borderwidth="2")
        self.Frame2_5.configure(relief="groove")
        self.Frame2_5.configure(background="#ffcab0")
        self.Frame2_5.configure(highlightbackground="#d9d9d9")
        self.Frame2_5.configure(highlightcolor="black")
        self.Frame2_6 = tk.Frame(self.Frame2_5)
        self.Frame2_6.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_6.configure(relief='groove')
        self.Frame2_6.configure(borderwidth="2")
        self.Frame2_6.configure(relief="groove")
        self.Frame2_6.configure(background="#ff8040")
        self.Frame2_6.configure(highlightbackground="#d9d9d9")
        self.Frame2_6.configure(highlightcolor="black")
        self.Frame2_7 = tk.Frame(self.Frame2_6)
        self.Frame2_7.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_7.configure(relief='groove')
        self.Frame2_7.configure(borderwidth="2")
        self.Frame2_7.configure(relief="groove")
        self.Frame2_7.configure(background="#ff8040")
        self.Frame2_7.configure(highlightbackground="#d9d9d9")
        self.Frame2_7.configure(highlightcolor="black")
        self.Frame2_8 = tk.Frame(self.Frame1)
        self.Frame2_8.place(relx=0.784, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_8.configure(relief='groove')
        self.Frame2_8.configure(borderwidth="2")
        self.Frame2_8.configure(relief="groove")
        self.Frame2_8.configure(background="#ffcab0")
        self.Frame2_8.configure(highlightbackground="#d9d9d9")
        self.Frame2_8.configure(highlightcolor="black")
        self.Frame2_10 = tk.Frame(self.Frame2_8)
        self.Frame2_10.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_10.configure(relief='groove')
        self.Frame2_10.configure(borderwidth="2")
        self.Frame2_10.configure(relief="groove")
        self.Frame2_10.configure(background="#ff8040")
        self.Frame2_10.configure(highlightbackground="#d9d9d9")
        self.Frame2_10.configure(highlightcolor="black")
        self.Frame2_11 = tk.Frame(self.Frame2_10)
        self.Frame2_11.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_11.configure(relief='groove')
        self.Frame2_11.configure(borderwidth="2")
        self.Frame2_11.configure(relief="groove")
        self.Frame2_11.configure(background="#ff8040")
        self.Frame2_11.configure(highlightbackground="#d9d9d9")
        self.Frame2_11.configure(highlightcolor="black")
        self.Frame2_9 = tk.Frame(self.Frame1)
        self.Frame2_9.place(relx=0.753, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_9.configure(relief='groove')
        self.Frame2_9.configure(borderwidth="2")
        self.Frame2_9.configure(relief="groove")
        self.Frame2_9.configure(background="#ffcab0")
        self.Frame2_9.configure(highlightbackground="#d9d9d9")
        self.Frame2_9.configure(highlightcolor="black")
        self.Frame2_10 = tk.Frame(self.Frame2_9)
        self.Frame2_10.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_10.configure(relief='groove')
        self.Frame2_10.configure(borderwidth="2")
        self.Frame2_10.configure(relief="groove")
        self.Frame2_10.configure(background="#ff8040")
        self.Frame2_10.configure(highlightbackground="#d9d9d9")
        self.Frame2_10.configure(highlightcolor="black")
        self.Frame2_11 = tk.Frame(self.Frame2_10)
        self.Frame2_11.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_11.configure(relief='groove')
        self.Frame2_11.configure(borderwidth="2")
        self.Frame2_11.configure(relief="groove")
        self.Frame2_11.configure(background="#ff8040")
        self.Frame2_11.configure(highlightbackground="#d9d9d9")
        self.Frame2_11.configure(highlightcolor="black")
        self.Frame2_12 = tk.Frame(self.Frame2_9)
        self.Frame2_12.place(relx=19.72, rely=5.4, relheight=1.0, relwidth=1.0)
        self.Frame2_12.configure(relief='groove')
        self.Frame2_12.configure(borderwidth="2")
        self.Frame2_12.configure(relief="groove")
        self.Frame2_12.configure(background="#ff8040")
        self.Frame2_12.configure(highlightbackground="#d9d9d9")
        self.Frame2_12.configure(highlightcolor="black")
        self.Frame2_13 = tk.Frame(self.Frame2_12)
        self.Frame2_13.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_13.configure(relief='groove')
        self.Frame2_13.configure(borderwidth="2")
        self.Frame2_13.configure(relief="groove")
        self.Frame2_13.configure(background="#ff8040")
        self.Frame2_13.configure(highlightbackground="#d9d9d9")
        self.Frame2_13.configure(highlightcolor="black")
        self.Frame2_14 = tk.Frame(self.Frame2_13)
        self.Frame2_14.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_14.configure(relief='groove')
        self.Frame2_14.configure(borderwidth="2")
        self.Frame2_14.configure(relief="groove")
        self.Frame2_14.configure(background="#ff8040")
        self.Frame2_14.configure(highlightbackground="#d9d9d9")
        self.Frame2_14.configure(highlightcolor="black")
        self.Frame2_12 = tk.Frame(self.Frame2_12)
        self.Frame2_12.place(relx=19.24, rely=6.2, relheight=1.0, relwidth=1.0)
        self.Frame2_12.configure(relief='groove')
        self.Frame2_12.configure(borderwidth="2")
        self.Frame2_12.configure(relief="groove")
        self.Frame2_12.configure(background="#ff8040")
        self.Frame2_12.configure(highlightbackground="#d9d9d9")
        self.Frame2_12.configure(highlightcolor="black")
        self.Frame2_13 = tk.Frame(self.Frame2_12)
        self.Frame2_13.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_13.configure(relief='groove')
        self.Frame2_13.configure(borderwidth="2")
        self.Frame2_13.configure(relief="groove")
        self.Frame2_13.configure(background="#ff8040")
        self.Frame2_13.configure(highlightbackground="#d9d9d9")
        self.Frame2_13.configure(highlightcolor="black")
        self.Frame2_15 = tk.Frame(self.Frame2_13)
        self.Frame2_15.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_15.configure(relief='groove')
        self.Frame2_15.configure(borderwidth="2")
        self.Frame2_15.configure(relief="groove")
        self.Frame2_15.configure(background="#ff8040")
        self.Frame2_15.configure(highlightbackground="#d9d9d9")
        self.Frame2_15.configure(highlightcolor="black")
        self.Frame2_15 = tk.Frame(self.Frame2_12)
        self.Frame2_15.place(relx=19.28, rely=4.667, relheight=1.0, relwidth=1.0)
        self.Frame2_15.configure(relief='groove')
        self.Frame2_15.configure(borderwidth="2")
        self.Frame2_15.configure(relief="groove")
        self.Frame2_15.configure(background="#ff8040")
        self.Frame2_15.configure(highlightbackground="#d9d9d9")
        self.Frame2_15.configure(highlightcolor="black")
        self.Frame2_16 = tk.Frame(self.Frame2_15)
        self.Frame2_16.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_16.configure(relief='groove')
        self.Frame2_16.configure(borderwidth="2")
        self.Frame2_16.configure(relief="groove")
        self.Frame2_16.configure(background="#ff8040")
        self.Frame2_16.configure(highlightbackground="#d9d9d9")
        self.Frame2_16.configure(highlightcolor="black")
        self.Frame2_17 = tk.Frame(self.Frame2_16)
        self.Frame2_17.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)
        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#ff8040")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")
        self.Frame2_15 = tk.Frame(self.Frame1)
        self.Frame2_15.place(relx=0.723, rely=0.452, relheight=0.097
                , relwidth=0.026)
        self.Frame2_15.configure(relief='groove')
        self.Frame2_15.configure(borderwidth="2")
        self.Frame2_15.configure(relief="groove")
        self.Frame2_15.configure(background="#ffcab0")
        self.Frame2_15.configure(highlightbackground="#d9d9d9")
        self.Frame2_15.configure(highlightcolor="black")
        self.Frame2_16 = tk.Frame(self.Frame2_15)
        self.Frame2_16.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)
        self.Frame2_16.configure(relief='groove')
        self.Frame2_16.configure(borderwidth="2")
        self.Frame2_16.configure(relief="groove")
        self.Frame2_16.configure(background="#ff8040")
        self.Frame2_16.configure(highlightbackground="#d9d9d9")
        self.Frame2_16.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame2_16)
        self.Frame2_17.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#ff8040")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_16 = tk.Frame(self.Frame1)
        self.Frame2_16.place(relx=0.738, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_16.configure(relief='groove')
        self.Frame2_16.configure(borderwidth="2")
        self.Frame2_16.configure(relief="groove")
        self.Frame2_16.configure(background="#f79b64")
        self.Frame2_16.configure(highlightbackground="#d9d9d9")
        self.Frame2_16.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame2_16)
        self.Frame2_17.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#ff8040")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame2_16)
        self.Frame2_17.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#fb5200")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame2_17)
        self.Frame2_17.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#fb5200")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame2_16)
        self.Frame2_17.place(relx=21.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#fb5200")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame1)
        self.Frame2_17.place(relx=0.8, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#f79b64")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.831, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#f79b64")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=25.4, rely=1.733, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.862, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#f79b64")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=26.8, rely=2.133, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.769, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#f79b64")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=26.84, rely=2.267, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.892, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#f79b64")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=28.76, rely=7.333, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_18)
        self.Frame2_20.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#fb5200")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_22 = tk.Frame(self.Frame2_21)
        self.Frame2_22.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_22.configure(relief='groove')
        self.Frame2_22.configure(borderwidth="2")
        self.Frame2_22.configure(relief="groove")
        self.Frame2_22.configure(background="#ff8040")
        self.Frame2_22.configure(highlightbackground="#d9d9d9")
        self.Frame2_22.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_20)
        self.Frame2_20.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#fb5200")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_22 = tk.Frame(self.Frame2_21)
        self.Frame2_22.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_22.configure(relief='groove')
        self.Frame2_22.configure(borderwidth="2")
        self.Frame2_22.configure(relief="groove")
        self.Frame2_22.configure(background="#ff8040")
        self.Frame2_22.configure(highlightbackground="#d9d9d9")
        self.Frame2_22.configure(highlightcolor="black")

        self.Frame2_17 = tk.Frame(self.Frame1)
        self.Frame2_17.place(relx=0.759, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_17.configure(relief='groove')
        self.Frame2_17.configure(borderwidth="2")
        self.Frame2_17.configure(relief="groove")
        self.Frame2_17.configure(background="#ff6820")
        self.Frame2_17.configure(highlightbackground="#d9d9d9")
        self.Frame2_17.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff8040")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_17)
        self.Frame2_18.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#fb5200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.79, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff6820")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=24.36, rely=1.4, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#9b3200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.821, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff6820")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.851, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff6820")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=26.28, rely=1.133, relheight=1.0, relwidth=1.0)

        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#9b3200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.882, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff6820")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame2_18)
        self.Frame2_18.place(relx=28.0, rely=1.333, relheight=1.0, relwidth=1.0)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#9b3200")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_18 = tk.Frame(self.Frame1)
        self.Frame2_18.place(relx=0.913, rely=0.194, relheight=0.097
                , relwidth=0.026)
        self.Frame2_18.configure(relief='groove')
        self.Frame2_18.configure(borderwidth="2")
        self.Frame2_18.configure(relief="groove")
        self.Frame2_18.configure(background="#ff6820")
        self.Frame2_18.configure(highlightbackground="#d9d9d9")
        self.Frame2_18.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#ff8040")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_18)
        self.Frame2_19.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame2_19)
        self.Frame2_19.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#fb5200")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_19 = tk.Frame(self.Frame1)
        self.Frame2_19.place(relx=0.923, rely=0.323, relheight=0.097
                , relwidth=0.026)
        self.Frame2_19.configure(relief='groove')
        self.Frame2_19.configure(borderwidth="2")
        self.Frame2_19.configure(relief="groove")
        self.Frame2_19.configure(background="#f79b64")
        self.Frame2_19.configure(highlightbackground="#d9d9d9")
        self.Frame2_19.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#ff8040")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_19)
        self.Frame2_20.place(relx=23.6, rely=2.667, relheight=1.0, relwidth=1.0)
        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#fb5200")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_22 = tk.Frame(self.Frame2_21)
        self.Frame2_22.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_22.configure(relief='groove')
        self.Frame2_22.configure(borderwidth="2")
        self.Frame2_22.configure(relief="groove")
        self.Frame2_22.configure(background="#ff8040")
        self.Frame2_22.configure(highlightbackground="#d9d9d9")
        self.Frame2_22.configure(highlightcolor="black")

        self.Frame2_20 = tk.Frame(self.Frame2_20)
        self.Frame2_20.place(relx=23.32, rely=2.467, relheight=1.0, relwidth=1.0)

        self.Frame2_20.configure(relief='groove')
        self.Frame2_20.configure(borderwidth="2")
        self.Frame2_20.configure(relief="groove")
        self.Frame2_20.configure(background="#fb5200")
        self.Frame2_20.configure(highlightbackground="#d9d9d9")
        self.Frame2_20.configure(highlightcolor="black")

        self.Frame2_21 = tk.Frame(self.Frame2_20)
        self.Frame2_21.place(relx=16.84, rely=2.333, relheight=1.0, relwidth=1.8)

        self.Frame2_21.configure(relief='groove')
        self.Frame2_21.configure(borderwidth="2")
        self.Frame2_21.configure(relief="groove")
        self.Frame2_21.configure(background="#ff8040")
        self.Frame2_21.configure(highlightbackground="#d9d9d9")
        self.Frame2_21.configure(highlightcolor="black")

        self.Frame2_22 = tk.Frame(self.Frame2_21)
        self.Frame2_22.place(relx=9.356, rely=2.333, relheight=1.0, relwidth=1.0)

        self.Frame2_22.configure(relief='groove')
        self.Frame2_22.configure(borderwidth="2")
        self.Frame2_22.configure(relief="groove")
        self.Frame2_22.configure(background="#ff8040")
        self.Frame2_22.configure(highlightbackground="#d9d9d9")
        self.Frame2_22.configure(highlightcolor="black")

        self.Label1_13 = tk.Label(self.Frame1)
        self.Label1_13.place(relx=0.144, rely=0.452, height=43, width=380)
        self.Label1_13.configure(activebackground="#f9f9f9")
        self.Label1_13.configure(activeforeground="black")
        self.Label1_13.configure(background="red")#0074e8
        self.Label1_13.configure(disabledforeground="#a3a3a3")
        self.Label1_13.configure(font="-family {Segoe UI Black} -size 18 -weight bold")
        self.Label1_13.configure(foreground="#ffffff")
        self.Label1_13.configure(highlightbackground="#d9d9d9")
        self.Label1_13.configure(highlightcolor="black")
        self.Label1_13.configure(text='''Digital Terrain Modeling''')

        self.Labelframe1 = tk.LabelFrame(top)
        self.Labelframe1.place(relx=0.009, rely=0.254, relheight=0.727
                , relwidth=0.977)
        self.Labelframe1.configure(relief='groove')
        self.Labelframe1.configure(foreground="black")
        self.Labelframe1.configure(text='''Summit Detector''')
        self.Labelframe1.configure(background="#d9d9d9")
        self.Labelframe1.configure(highlightbackground="#d9d9d9")
        self.Labelframe1.configure(highlightcolor="black")

        self.Labelframe2 = tk.LabelFrame(self.Labelframe1)
        self.Labelframe2.place(relx=0.011, rely=0.042, relheight=0.179
                , relwidth=0.979, bordermode='ignore')
        self.Labelframe2.configure(relief='groove')
        self.Labelframe2.configure(foreground="#000000")
        self.Labelframe2.configure(text='''Input Raster''')
        self.Labelframe2.configure(background="#d9d9d9")
        self.Labelframe2.configure(highlightbackground="#d9d9d9")
        self.Labelframe2.configure(highlightcolor="black")

        self.Label2 = tk.Label(self.Labelframe2)
        self.Label2.place(relx=0.021, rely=0.353, height=21, width=69
                , bordermode='ignore')
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Input Raster''')

        self.Entry1 = tk.Entry(self.Labelframe2)
        self.Entry1.place(relx=0.098, rely=0.388, height=20, relwidth=0.457
                , bordermode='ignore')
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="#c4c4c4")
        self.Entry1.configure(selectforeground="black")
        # -------------------------------------------------------------
        pathInputRaster = StringVar()
        self.Entry1.configure(textvariable = pathInputRaster)
        # -------------------------------------------------------------
        
        self.Button1 = tk.Button(self.Labelframe2)
        self.Button1.place(relx=0.566, rely=0.365, height=24, width=67
                , bordermode='ignore')
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''Browse''')
        # -------------------------------------------------------------
        self.Button1.configure(command = get_inputRaster_path)
        # -------------------------------------------------------------
        
        self.Label3 = tk.Label(self.Labelframe2)
        self.Label3.place(relx=0.652, rely=0.376, height=21, width=250
                , bordermode='ignore')
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#75baff")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''Acceptable Raster Format: .tif  or .asc or .txt''')

        self.Label3_7 = tk.Label(self.Labelframe2)
        self.Label3_7.place(relx=0.015, rely=0.659, height=21, width=131
                , bordermode='ignore')
        self.Label3_7.configure(activebackground="#f9f9f9")
        self.Label3_7.configure(activeforeground="black")
        self.Label3_7.configure(background="#d9d9d9")
        self.Label3_7.configure(disabledforeground="#a3a3a3")
        self.Label3_7.configure(foreground="#75baff")
        self.Label3_7.configure(highlightbackground="#d9d9d9")
        self.Label3_7.configure(highlightcolor="black")
        self.Label3_7.configure(text='''Input Raster File Path''')

        self.Labelframe3 = tk.LabelFrame(self.Labelframe1)
        self.Labelframe3.place(relx=0.011, rely=0.232, relheight=0.179
                , relwidth=0.979, bordermode='ignore')
        self.Labelframe3.configure(relief='groove')
        self.Labelframe3.configure(foreground="black")
        self.Labelframe3.configure(text='''Moving Window Dimension''')
        self.Labelframe3.configure(background="#d9d9d9")
        self.Labelframe3.configure(highlightbackground="#d9d9d9")
        self.Labelframe3.configure(highlightcolor="black")

        self.Label4 = tk.Label(self.Labelframe3)
        self.Label4.place(relx=0.013, rely=0.353, height=21, width=51
                , bordermode='ignore')
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''Row size''')

        self.Entry2 = tk.Entry(self.Labelframe3)
        self.Entry2.place(relx=0.068, rely=0.376, height=20, relwidth=0.173
                , bordermode='ignore')
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="#c4c4c4")
        self.Entry2.configure(selectforeground="black")
        # ----------------------------------------------------------
        rowDimension = StringVar()
        self.Entry2.configure(textvariable = rowDimension)
        # ----------------------------------------------------------

        self.Label5 = tk.Label(self.Labelframe3)
        self.Label5.place(relx=0.426, rely=0.376, height=21, width=74
                , bordermode='ignore')
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''Column Size''')

        self.Entry3 = tk.Entry(self.Labelframe3)
        self.Entry3.place(relx=0.512, rely=0.4, height=20, relwidth=0.173
                , bordermode='ignore')
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="#c4c4c4")
        self.Entry3.configure(selectforeground="black")
        # ----------------------------------------------------------
        columnDimension = StringVar()
        self.Entry3.configure(textvariable = columnDimension)
        # ----------------------------------------------------------
        
        self.Button2 = tk.Button(self.Labelframe3)
        self.Button2.place(relx=0.873, rely=0.318, height=34, width=97
                , bordermode='ignore')
        self.Button2.configure(activebackground="#ececec")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#5eaeff")
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(font="-family {Segoe UI} -size 9 -weight bold")
        self.Button2.configure(foreground="#ffffff")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Show Window''')
        # ----------------------------------------------------------
        self.Button2.configure(command = show_MovingWindow)
        # ----------------------------------------------------------
        
        self.Label6 = tk.Label(self.Labelframe3)
        self.Label6.place(relx=0.014, rely=0.682, height=21, width=176
                , bordermode='ignore')
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(activeforeground="black")
        self.Label6.configure(background="#d9d9d9")
        self.Label6.configure(disabledforeground="#a3a3a3")
        self.Label6.configure(foreground="#adadad")
        self.Label6.configure(highlightbackground="#d9d9d9")
        self.Label6.configure(highlightcolor="black")
        self.Label6.configure(text='''Row size of the Moving Window''')

        self.Message1_8 = tk.Message(self.Labelframe3)
        self.Message1_8.place(relx=0.692, rely=0.235, relheight=0.624
                , relwidth=0.168, bordermode='ignore')
        self.Message1_8.configure(background="#d9d9d9")
        self.Message1_8.configure(foreground="#75baff")
        self.Message1_8.configure(highlightbackground="#d9d9d9")
        self.Message1_8.configure(highlightcolor="black")
        self.Message1_8.configure(text='''Moving Window Column Size
should be a positive
odd number''')
        self.Message1_8.configure(width=160)

        self.Label6_14 = tk.Label(self.Labelframe3)
        self.Label6_14.place(relx=0.426, rely=0.706, height=21, width=176
                , bordermode='ignore')
        self.Label6_14.configure(activebackground="#f9f9f9")
        self.Label6_14.configure(activeforeground="black")
        self.Label6_14.configure(background="#d9d9d9")
        self.Label6_14.configure(disabledforeground="#a3a3a3")
        self.Label6_14.configure(foreground="#adadad")
        self.Label6_14.configure(highlightbackground="#d9d9d9")
        self.Label6_14.configure(highlightcolor="black")
        self.Label6_14.configure(text='''Column size of the Moving Window''')

        self.Message1_9 = tk.Message(self.Labelframe3)
        self.Message1_9.place(relx=0.253, rely=0.235, relheight=0.624
                , relwidth=0.168, bordermode='ignore')
        self.Message1_9.configure(background="#d9d9d9")
        self.Message1_9.configure(foreground="#75baff")
        self.Message1_9.configure(highlightbackground="#d9d9d9")
        self.Message1_9.configure(highlightcolor="black")
        self.Message1_9.configure(text='''Moving Window Column Size
should be a positive
odd number''')
        self.Message1_9.configure(width=160)

        self.Labelframe4 = tk.LabelFrame(self.Labelframe1)
        self.Labelframe4.place(relx=0.01, rely=0.547, relheight=0.263
                , relwidth=0.979, bordermode='ignore')
        self.Labelframe4.configure(relief='groove')
        self.Labelframe4.configure(foreground="black")
        self.Labelframe4.configure(text='''Output Characterization''')
        self.Labelframe4.configure(background="#d9d9d9")
        self.Labelframe4.configure(highlightbackground="#d9d9d9")
        self.Labelframe4.configure(highlightcolor="black")

        self.Label7 = tk.Label(self.Labelframe4)
        self.Label7.place(relx=0.009, rely=0.24, height=21, width=79
                , bordermode='ignore')
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background="#d9d9d9")
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(text='''Threshold (%)''')

        self.Entry4 = tk.Entry(self.Labelframe4)
        self.Entry4.place(relx=0.095, rely=0.24, height=20, relwidth=0.078
                , bordermode='ignore')
        self.Entry4.configure(background="white")
        self.Entry4.configure(disabledforeground="#a3a3a3")
        self.Entry4.configure(font="TkFixedFont")
        self.Entry4.configure(foreground="#000000")
        self.Entry4.configure(highlightbackground="#d9d9d9")
        self.Entry4.configure(highlightcolor="black")
        self.Entry4.configure(insertbackground="black")
        self.Entry4.configure(selectbackground="#c4c4c4")
        self.Entry4.configure(selectforeground="black")
        # -------------------------------------------------------------------
        Threshold_algorithm = StringVar()
        self.Entry4.configure(textvariable = Threshold_algorithm)
        # -------------------------------------------------------------------
        
        self.Label8 = tk.Label(self.Labelframe4)
        self.Label8.place(relx=0.551, rely=0.72, height=21, width=112
                , bordermode='ignore')
        self.Label8.configure(activebackground="#f9f9f9")
        self.Label8.configure(activeforeground="black")
        self.Label8.configure(background="#d9d9d9")
        self.Label8.configure(disabledforeground="#a3a3a3")
        self.Label8.configure(foreground="#000000")
        self.Label8.configure(highlightbackground="#d9d9d9")
        self.Label8.configure(highlightcolor="black")
        self.Label8.configure(text='''Output Raster Path''')

        self.Entry5 = tk.Entry(self.Labelframe4)
        self.Entry5.place(relx=0.675, rely=0.72, height=20, relwidth=0.141
                , bordermode='ignore')
        self.Entry5.configure(background="white")
        self.Entry5.configure(disabledforeground="#a3a3a3")
        self.Entry5.configure(font="TkFixedFont")
        self.Entry5.configure(foreground="#000000")
        self.Entry5.configure(highlightbackground="#d9d9d9")
        self.Entry5.configure(highlightcolor="black")
        self.Entry5.configure(insertbackground="black")
        self.Entry5.configure(selectbackground="#c4c4c4")
        self.Entry5.configure(selectforeground="black")
        # -------------------------------------------------------------------
        Output_raster_Path_File = StringVar()
        self.Entry5.configure(textvariable = Output_raster_Path_File)
        # -------------------------------------------------------------------
        
        self.Button3 = tk.Button(self.Labelframe4)
        self.Button3.place(relx=0.824, rely=0.72, height=24, width=67
                , bordermode='ignore')
        self.Button3.configure(activebackground="#ececec")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#d9d9d9")
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''Browse''')
        # ------------------------------------------------------------------
        self.Button3.configure(command = get_out_raster_path)
        # ------------------------------------------------------------------
        
        self.Message2 = tk.Message(self.Labelframe4)
        self.Message2.place(relx=0.179, rely=0.112, relheight=0.384
                , relwidth=0.212, bordermode='ignore')
        self.Message2.configure(background="#d9d9d9")
        self.Message2.configure(foreground="#75baff")
        self.Message2.configure(highlightbackground="#d9d9d9")
        self.Message2.configure(highlightcolor="black")
        self.Message2.configure(text='''Enter a Threshold in range of 0-100 for Detecting Summits''')
        self.Message2.configure(width=201)

        self.Label12 = tk.Label(self.Labelframe4)
        self.Label12.place(relx=0.009, rely=0.72, height=21, width=144
                , bordermode='ignore')
        self.Label12.configure(activebackground="#f9f9f9")
        self.Label12.configure(activeforeground="black")
        self.Label12.configure(background="#d9d9d9")
        self.Label12.configure(disabledforeground="#a3a3a3")
        self.Label12.configure(foreground="#000000")
        self.Label12.configure(highlightbackground="#d9d9d9")
        self.Label12.configure(highlightcolor="black")
        self.Label12.configure(text='''Summit Points Output File''')

        self.Entry10 = tk.Entry(self.Labelframe4)
        self.Entry10.place(relx=0.168, rely=0.72, height=20, relwidth=0.141
                , bordermode='ignore')
        self.Entry10.configure(background="white")
        self.Entry10.configure(disabledforeground="#a3a3a3")
        self.Entry10.configure(font="TkFixedFont")
        self.Entry10.configure(foreground="#000000")
        self.Entry10.configure(highlightbackground="#d9d9d9")
        self.Entry10.configure(highlightcolor="black")
        self.Entry10.configure(insertbackground="black")
        self.Entry10.configure(selectbackground="#c4c4c4")
        self.Entry10.configure(selectforeground="black")
        # -------------------------------------------------------------------
        Output_vector_Path_File = StringVar()
        self.Entry10.configure(textvariable = Output_vector_Path_File)
        # -------------------------------------------------------------------
         
        self.Button8 = tk.Button(self.Labelframe4)
        self.Button8.place(relx=0.316, rely=0.72, height=24, width=67
                , bordermode='ignore')
        self.Button8.configure(activebackground="#ececec")
        self.Button8.configure(activeforeground="#000000")
        self.Button8.configure(background="#d9d9d9")
        self.Button8.configure(disabledforeground="#a3a3a3")
        self.Button8.configure(foreground="#000000")
        self.Button8.configure(highlightbackground="#d9d9d9")
        self.Button8.configure(highlightcolor="black")
        self.Button8.configure(pady="0")
        self.Button8.configure(text='''Browse''')
        # -------------------------------------------------------------------
        self.Button8.configure(command = get_out_Vector_path)
        # -------------------------------------------------------------------
        
        self.Message2_12 = tk.Message(self.Labelframe4)
        self.Message2_12.place(relx=0.388, rely=0.72, relheight=0.144
                , relwidth=0.148, bordermode='ignore')
        self.Message2_12.configure(background="#d9d9d9")
        self.Message2_12.configure(foreground="#75baff")
        self.Message2_12.configure(highlightbackground="#d9d9d9")
        self.Message2_12.configure(highlightcolor="black")
        self.Message2_12.configure(text='''.shp and .txt File Format''')
        self.Message2_12.configure(width=141)

        self.Message2_13 = tk.Message(self.Labelframe4)
        self.Message2_13.place(relx=0.899, rely=0.72, relheight=0.144
                , relwidth=0.096, bordermode='ignore')
        self.Message2_13.configure(background="#d9d9d9")
        self.Message2_13.configure(foreground="#75baff")
        self.Message2_13.configure(highlightbackground="#d9d9d9")
        self.Message2_13.configure(highlightcolor="black")
        self.Message2_13.configure(text='''.asc File Format''')
        self.Message2_13.configure(width=91)

        self.Label7_22 = tk.Label(self.Labelframe4)
        self.Label7_22.place(relx=0.418, rely=0.2, height=21, width=109
                , bordermode='ignore')
        self.Label7_22.configure(activebackground="#f9f9f9")
        self.Label7_22.configure(activeforeground="black")
        self.Label7_22.configure(background="#d9d9d9")
        self.Label7_22.configure(disabledforeground="#a3a3a3")
        self.Label7_22.configure(foreground="#000000")
        self.Label7_22.configure(highlightbackground="#d9d9d9")
        self.Label7_22.configure(highlightcolor="black")
        self.Label7_22.configure(text='''Elevation Threshold''')

        self.Entry4_23 = tk.Entry(self.Labelframe4)
        self.Entry4_23.place(relx=0.537, rely=0.216, height=20, relwidth=0.078
                , bordermode='ignore')
        self.Entry4_23.configure(background="white")
        self.Entry4_23.configure(disabledforeground="#a3a3a3")
        self.Entry4_23.configure(font="TkFixedFont")
        self.Entry4_23.configure(foreground="#000000")
        self.Entry4_23.configure(highlightbackground="#d9d9d9")
        self.Entry4_23.configure(highlightcolor="black")
        self.Entry4_23.configure(insertbackground="black")
        self.Entry4_23.configure(selectbackground="#c4c4c4")
        self.Entry4_23.configure(selectforeground="black")
        # ----------------------------------------------------------------------
        Elevation_Threshold = StringVar()
        self.Entry4_23.configure(textvariable = Elevation_Threshold)
        # ----------------------------------------------------------------------
        self.Message2_24 = tk.Message(self.Labelframe4)
        self.Message2_24.place(relx=0.617, rely=0.088, relheight=0.384
                , relwidth=0.306, bordermode='ignore')
        self.Message2_24.configure(background="#d9d9d9")
        self.Message2_24.configure(foreground="#75baff")
        self.Message2_24.configure(highlightbackground="#d9d9d9")
        self.Message2_24.configure(highlightcolor="black")
        self.Message2_24.configure(text='''Elevation Threshold should be grather than Min-value 
and less than Max-value''')
        self.Message2_24.configure(width=291)

        self.Label7_23 = tk.Label(self.Labelframe4)
        self.Label7_23.place(relx=0.441, rely=0.456, height=21, width=89
                , bordermode='ignore')
        self.Label7_23.configure(activebackground="#f9f9f9")
        self.Label7_23.configure(activeforeground="black")
        self.Label7_23.configure(background="#d9d9d9")
        self.Label7_23.configure(disabledforeground="#a3a3a3")
        self.Label7_23.configure(foreground="#000000")
        self.Label7_23.configure(highlightbackground="#d9d9d9")
        self.Label7_23.configure(highlightcolor="black")
        self.Label7_23.configure(text='''Min-Elevation:''')

        self.Label7_24 = tk.Label(self.Labelframe4)
        self.Label7_24.place(relx=0.599, rely=0.448, height=21, width=89
                , bordermode='ignore')
        self.Label7_24.configure(activebackground="#f9f9f9")
        self.Label7_24.configure(activeforeground="black")
        self.Label7_24.configure(background="#d9d9d9")
        self.Label7_24.configure(disabledforeground="#a3a3a3")
        self.Label7_24.configure(foreground="#000000")
        self.Label7_24.configure(highlightbackground="#d9d9d9")
        self.Label7_24.configure(highlightcolor="black")
        self.Label7_24.configure(text='''Max-Elevation:''')

        self.Entry4_24 = tk.Entry(self.Labelframe4)
        self.Entry4_24.place(relx=0.534, rely=0.464, height=20, relwidth=0.057
                , bordermode='ignore')
        self.Entry4_24.configure(background="#d8d8d8")
        self.Entry4_24.configure(disabledforeground="#a3a3a3")
        self.Entry4_24.configure(font="TkFixedFont")
        self.Entry4_24.configure(foreground="#000000")
        self.Entry4_24.configure(highlightbackground="#d9d9d9")
        self.Entry4_24.configure(highlightcolor="black")
        self.Entry4_24.configure(insertbackground="black")
        self.Entry4_24.configure(selectbackground="#c4c4c4")
        self.Entry4_24.configure(selectforeground="black")
        # --------------------------------------------------------
        minElevs= StringVar()
        self.Entry4_24.configure(textvariable = minElevs)
        # --------------------------------------------------------
        
        self.Entry4_25 = tk.Entry(self.Labelframe4)
        self.Entry4_25.place(relx=0.693, rely=0.464, height=20, relwidth=0.057
                , bordermode='ignore')
        self.Entry4_25.configure(background="#d8d8d8")
        self.Entry4_25.configure(disabledforeground="#a3a3a3")
        self.Entry4_25.configure(font="TkFixedFont")
        self.Entry4_25.configure(foreground="#000000")
        self.Entry4_25.configure(highlightbackground="#d9d9d9")
        self.Entry4_25.configure(highlightcolor="black")
        self.Entry4_25.configure(insertbackground="black")
        self.Entry4_25.configure(selectbackground="#c4c4c4")
        self.Entry4_25.configure(selectforeground="black")
        # --------------------------------------------------------
        maxElevs= StringVar()
        self.Entry4_25.configure(textvariable = maxElevs )
        # --------------------------------------------------------
        
        self.Labelframe6 = tk.LabelFrame(self.Labelframe1)
        self.Labelframe6.place(relx=0.01, rely=0.819, relheight=0.158
                , relwidth=0.454, bordermode='ignore')
        self.Labelframe6.configure(relief='groove')
        self.Labelframe6.configure(foreground="black")
        self.Labelframe6.configure(text='''window''')
        self.Labelframe6.configure(background="#d9d9d9")
        self.Labelframe6.configure(highlightbackground="#d9d9d9")
        self.Labelframe6.configure(highlightcolor="black")

        self.Button7 = tk.Button(self.Labelframe6)
        self.Button7.place(relx=0.032, rely=0.267, height=44, width=77
                , bordermode='ignore')
        self.Button7.configure(activebackground="#ececec")
        self.Button7.configure(activeforeground="#000000")
        self.Button7.configure(background="#d7d7ff")
        self.Button7.configure(disabledforeground="#a3a3a3")
        self.Button7.configure(font="-family {Segoe UI} -size 9 -weight bold")
        self.Button7.configure(foreground="#000000")
        self.Button7.configure(highlightbackground="#d9d9d9")
        self.Button7.configure(highlightcolor="black")
        self.Button7.configure(pady="0")
        self.Button7.configure(text='''Close''')
        # ------------------------------------------------------------
        self.Button7.configure(command = destroy_window)
        # ------------------------------------------------------------
        
        self.Button5 = tk.Button(self.Labelframe6)
        self.Button5.place(relx=0.22, rely=0.267, height=44, width=87
                , bordermode='ignore')
        self.Button5.configure(activebackground="#ececec")
        self.Button5.configure(activeforeground="#000000")
        self.Button5.configure(background="#006cd9")
        self.Button5.configure(disabledforeground="#a3a3a3")
        self.Button5.configure(font="-family {Segoe UI} -size 9 -weight bold")
        self.Button5.configure(foreground="#ffffff")
        self.Button5.configure(highlightbackground="#d9d9d9")
        self.Button5.configure(highlightcolor="black")
        self.Button5.configure(pady="0")
        self.Button5.configure(text='''Run Model''')
        # ------------------------------------------------------------------
        self.Button5.configure(command = MainRun)
        # ------------------------------------------------------------------

        self.Message1_10 = tk.Message(self.Labelframe6)
        self.Message1_10.place(relx=0.664, rely=0.267, relheight=0.573
                , relwidth=0.318, bordermode='ignore')
        self.Message1_10.configure(background="#d9d9d9")
        self.Message1_10.configure(foreground="#808080")
        self.Message1_10.configure(highlightbackground="#d9d9d9")
        self.Message1_10.configure(highlightcolor="black")
        self.Message1_10.configure(text='''First Click Run Model
then Click Landform Classify''')
        self.Message1_10.configure(width=140)

        self.TProgressbar1 = ttk.Progressbar(self.Labelframe1)
        self.TProgressbar1.place(relx=0.536, rely=0.888, relwidth=0.402
                , relheight=0.0, height=25, bordermode='ignore')
        # -------------------------------------------------------------------------------
        def ProgressBar(r,r_number):
            ProgressPercent = (float(r)/float(r_number))*100.0
            self.TProgressbar1.configure(value = ProgressPercent)
            ProgressValue.set(int(ProgressPercent))
            top.update_idletasks()        
        # -------------------------------------------------------------------------------

        self.Label10 = tk.Label(self.Labelframe1)
        self.Label10.place(relx=0.471, rely=0.893, height=21, width=59
                , bordermode='ignore')
        self.Label10.configure(activebackground="#f9f9f9")
        self.Label10.configure(activeforeground="black")
        self.Label10.configure(background="#d9d9d9")
        self.Label10.configure(disabledforeground="#a3a3a3")
        self.Label10.configure(foreground="#000000")
        self.Label10.configure(highlightbackground="#d9d9d9")
        self.Label10.configure(highlightcolor="black")
        self.Label10.configure(text='''Progress''')

        self.Entry8 = tk.Entry(self.Labelframe1)
        self.Entry8.place(relx=0.946, rely=0.888, height=25, relwidth=0.035
                , bordermode='ignore')
        self.Entry8.configure(background="#f2f2f2")
        self.Entry8.configure(disabledforeground="#a3a3a3")
        self.Entry8.configure(font="TkFixedFont")
        self.Entry8.configure(foreground="#000000")
        self.Entry8.configure(highlightbackground="#d9d9d9")
        self.Entry8.configure(highlightcolor="black")
        self.Entry8.configure(insertbackground="black")
        self.Entry8.configure(relief="flat")
        self.Entry8.configure(selectbackground="#c4c4c4")
        self.Entry8.configure(selectforeground="black")

        # -------------------------------------------------------------------------------
        ProgressValue = StringVar()
        self.Entry8.configure(textvariable = ProgressValue)
        # -------------------------------------------------------------------------------
        
        self.Labelframe5 = tk.LabelFrame(self.Labelframe1)
        self.Labelframe5.place(relx=0.01, rely=0.421, relheight=0.116
                , relwidth=0.979, bordermode='ignore')
        self.Labelframe5.configure(relief='groove')
        self.Labelframe5.configure(foreground="#000000")
        self.Labelframe5.configure(text='''Algorithms''')
        self.Labelframe5.configure(background="#cdcdcd")
        self.Labelframe5.configure(highlightbackground="#d9d9d9")
        self.Labelframe5.configure(highlightcolor="#808080")

        self.Radiobutton1 = tk.Radiobutton(self.Labelframe5)
        self.Radiobutton1.place(relx=0.03, rely=0.436, relheight=0.455
                , relwidth=0.083, bordermode='ignore')
        self.Radiobutton1.configure(activebackground="#cdcdcd")
        self.Radiobutton1.configure(activeforeground="#000000")
        self.Radiobutton1.configure(background="#cdcdcd")
        self.Radiobutton1.configure(disabledforeground="#a3a3a3")
        self.Radiobutton1.configure(foreground="#000000")
        self.Radiobutton1.configure(highlightbackground="#d9d9d9")
        self.Radiobutton1.configure(highlightcolor="black")
        self.Radiobutton1.configure(justify='left')
        self.Radiobutton1.configure(text='''SMRS (%)''')
        self.Radiobutton1.configure(variable=Landform_Classifier_support.selectedButton)
        # ---------------------------------------------------------------------------------
        Algorithm_Number = IntVar()
        self.Radiobutton1.configure(value=1)
        self.Radiobutton1.configure(variable= Algorithm_Number)
        # ---------------------------------------------------------------------------------

        self.Radiobutton2 = tk.Radiobutton(self.Labelframe5)
        self.Radiobutton2.place(relx=0.285, rely=0.436, relheight=0.455
                , relwidth=0.086, bordermode='ignore')
        self.Radiobutton2.configure(activebackground="#ececec")
        self.Radiobutton2.configure(activeforeground="#000000")
        self.Radiobutton2.configure(background="#cdcdcd")
        self.Radiobutton2.configure(disabledforeground="#a3a3a3")
        self.Radiobutton2.configure(foreground="#000000")
        self.Radiobutton2.configure(highlightbackground="#d9d9d9")
        self.Radiobutton2.configure(highlightcolor="black")
        self.Radiobutton2.configure(justify='left')
        self.Radiobutton2.configure(text='''CMRS (%)''')
        self.Radiobutton2.configure(variable=Landform_Classifier_support.selectedButton)
        # ---------------------------------------------------------------------------------
        self.Radiobutton2.configure(value=2)
        self.Radiobutton2.configure(variable= Algorithm_Number)
        # ---------------------------------------------------------------------------------
        
        self.Radiobutton3 = tk.Radiobutton(self.Labelframe5)
        self.Radiobutton3.place(relx=0.55, rely=0.436, relheight=0.455
                , relwidth=0.077, bordermode='ignore')
        self.Radiobutton3.configure(activebackground="#ececec")
        self.Radiobutton3.configure(activeforeground="#000000")
        self.Radiobutton3.configure(background="#cdcdcd")
        self.Radiobutton3.configure(disabledforeground="#a3a3a3")
        self.Radiobutton3.configure(foreground="#000000")
        self.Radiobutton3.configure(highlightbackground="#d9d9d9")
        self.Radiobutton3.configure(highlightcolor="black")
        self.Radiobutton3.configure(justify='left')
        self.Radiobutton3.configure(text='''CPRS (%)''')
        self.Radiobutton3.configure(variable=Landform_Classifier_support.selectedButton)
        # ---------------------------------------------------------------------------------
        self.Radiobutton3.configure(value=3)
        self.Radiobutton3.configure(variable= Algorithm_Number)
        # ---------------------------------------------------------------------------------
        ##### New Added
        # ---------------------------------------------------------------------------------

        self.Radiobutton4 = tk.Radiobutton(self.Labelframe5)
        self.Radiobutton4.place(relx=0.8, rely=0.436, relheight=0.455
                                , relwidth=0.067, bordermode='ignore')
        self.Radiobutton4.configure(activebackground="#ececec")
        self.Radiobutton4.configure(activeforeground="#000000")
        self.Radiobutton4.configure(background="#cdcdcd")
        self.Radiobutton4.configure(disabledforeground="#a3a3a3")
        self.Radiobutton4.configure(foreground="#000000")
        self.Radiobutton4.configure(highlightbackground="#d9d9d9")
        self.Radiobutton4.configure(highlightcolor="black")
        self.Radiobutton4.configure(justify='left')
        self.Radiobutton4.configure(text='''TPI (%)''')
        self.Radiobutton4.configure(variable=Landform_Classifier_support.selectedButton)
        # ---------------------------------------------------------------------------------
        self.Radiobutton4.configure(value=4)
        self.Radiobutton4.configure(variable=Algorithm_Number)
        # ---------------------------------------------------------------------------------
        def ShowResult():
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches

            HeadEr = open(Output_raster_Path_File.get() + '/'+'Ridgelines_'+str(AN)+'_WinSize_'+str(Dim)+'.asc','r')
            Classification = open(Output_raster_Path_File.get() + '/'+'Ridgelines_'+str(AN)+'_WinSize_'+str(Dim)+'Classification.asc','a+')
            HeaderLists = []
            nline = 0
            for i in HeadEr:
                nline +=1
                if nline <= 6:
                    HeaderLists.append(i)
            for i in HeaderLists:
                Classification.write(i)
            Algorithms_Results = numpy.loadtxt(Output_raster_Path_File.get() + '/'+'Ridgelines_'+str(AN)+'_WinSize_'+str(Dim)+'.asc',skiprows = 6)
            path = pathInputRaster.get()

            if path.endswith('.tif'):
                from PIL import Image
                tiff_raster = Image.open(path)
                DEM = numpy.array(tiff_raster)
            elif path.endswith('.asc') or path.endswith('.txt'):                    
                DEM = numpy.loadtxt(path,skiprows = 6)
            rows = DEM.shape[0]
            columns = DEM.shape[1]
            maximumValue_DEM = numpy.max(DEM)
            minimumValue_DEM = maximumValue_DEM
            for i in DEM:
              for j in i:
                if j != -9999.0:
                  if j < minimumValue_DEM:
                    minimumValue_DEM = j

            maximumValue_DEM = float(maximumValue_DEM)
            minimumValue_DEM = float(minimumValue_DEM)
    
            N = int((int(rowDimension.get())-1)/2.0)
            r_code = -1   
            for r in range(rows - (int(rowDimension.get())-1)):
              ProgressBar(r,rows - (int(rowDimension.get())-1))
              r_code += 1
              c_code = -1 
              for c in range(columns - (int(rowDimension.get())-1)):
                c_code += 1
                cellValue = float(DEM[r_code+N,c_code+N])
                percentValue_elevs = 100.0 * ((cellValue - minimumValue_DEM) / (maximumValue_DEM - minimumValue_DEM ))
                if percentValue_elevs >=0.0 and percentValue_elevs<20.0:
                  elevs_code = 1
                if percentValue_elevs >=20.0 and percentValue_elevs<40.0:
                  elevs_code = 2
                if percentValue_elevs >=40.0 and percentValue_elevs<60.0:
                  elevs_code = 3
                if percentValue_elevs >=60.0 and percentValue_elevs<80.0:
                  elevs_code = 4
                if percentValue_elevs >=80.0 and percentValue_elevs<=100.0:
                  elevs_code = 5
                percent = Algorithms_Results[r_code - int((int(rowDimension.get())-1)/2.0),c_code - int((int(rowDimension.get())-1)/2.0)]
                if percent >= 0.0 and percent <20.0:
                    algorithm_code = 1
                if percent >=20.0 and percent < 40.0:
                    algorithm_code = 2
                if percent >=40.0 and percent < 60.0:
                    algorithm_code = 3
                if percent >=60.0 and percent < 80.0:
                    algorithm_code = 4
                if percent >=80.0 and percent <= 100.0:
                    algorithm_code = 5
                Classification.write(str(algorithm_code)+str(elevs_code)+' ')
              Classification.write('\n')
            Classification.close()  
            #print Output_raster_Path_File.get() + '/'+'Ridgelines_'+str(AN)+'_WinSize_'+str(Dim)+'Classification.asc'
            raster = numpy.loadtxt(Output_raster_Path_File.get() + '/'+'Ridgelines_'+str(AN)+'_WinSize_'+str(Dim)+'Classification.asc',skiprows = 6)
            list_new_structure = []
            for r in range(raster.shape[0]):
              ProgressBar(r,raster.shape[0])
              list_new_structure_row = []
              for c in range(raster.shape[1]):
                if raster[r,c] == 55:
                  list_new_structure_row.append([0,0,0])
                elif raster[r,c] == 54:
                  list_new_structure_row.append([97,0,0])
                elif raster[r,c] == 53:
                  list_new_structure_row.append([161,0,16])
                elif raster[r,c] == 52:
                  list_new_structure_row.append([221,0,0])
                elif raster[r,c] == 51:
                  list_new_structure_row.append([255,102,51])
                elif raster[r,c] == 45:
                  list_new_structure_row.append([102,49,3])
                elif raster[r,c] == 44:
                  list_new_structure_row.append([192,128,0])
                elif raster[r,c] == 43:
                  list_new_structure_row.append([238,158,0])
                elif raster[r,c] == 42:
                  list_new_structure_row.append([249,200,38])
                elif raster[r,c] == 41:
                  list_new_structure_row.append([254,212,85])
                elif raster[r,c] == 35:
                  list_new_structure_row.append([250,250,0])
                elif raster[r,c] == 34:
                  list_new_structure_row.append([255,255,87])
                elif raster[r,c] == 33:
                  list_new_structure_row.append([255,255,160])      
                elif raster[r,c] == 32:
                  list_new_structure_row.append([255,255,190])
                elif raster[r,c] == 31:
                  list_new_structure_row.append([255,255,255])
                elif raster[r,c] == 25:
                  list_new_structure_row.append([56,168,0])
                elif raster[r,c] == 24:
                  list_new_structure_row.append([76,230,0])
                elif raster[r,c] == 23:
                  list_new_structure_row.append([85,255,255])
                elif raster[r,c] == 22:
                  list_new_structure_row.append([163,255,115])
                elif raster[r,c] == 21:
                  list_new_structure_row.append([211,255,190])
                elif raster[r,c] == 15:
                  list_new_structure_row.append([190,232,230])
                elif raster[r,c] == 14:
                  list_new_structure_row.append([115,223,255])
                elif raster[r,c] == 13:
                  list_new_structure_row.append([0,197,255])
                elif raster[r,c] == 12:
                  list_new_structure_row.append([0,92,255])
                elif raster[r,c] == 11:
                  list_new_structure_row.append([0,38,115])   
              list_new_structure.append(list_new_structure_row)
            list_new_structure = numpy.array(list_new_structure)
            plt.figure(figsize=(10,6))
            box_1 = mpatches.Patch(color=(0,0,0), label='H5C5')
            box_2 = mpatches.Patch(color=(97/255.0,0,0), label='H5C4')
            box_3 = mpatches.Patch(color=(161/255.0,0,16/255.0), label='H5C3')
            box_4 = mpatches.Patch(color=(221/255.0,0,0), label='H5C2')
            box_5 = mpatches.Patch(color=(255/255.0,102/255.0,51/255.0), label='H5C1')
            box_6 = mpatches.Patch(color=(102/255.0,49/255.0,3/255.0), label='H4C5')
            box_7 = mpatches.Patch(color=(192/255.0,128/255.0,0), label='H4C4')
            box_8 = mpatches.Patch(color=(238/255.0,158/255.0,0), label='H4C3')
            box_9 = mpatches.Patch(color=(249/255.0,200/255.0,38/255.0), label='H4C2')
            box_10 = mpatches.Patch(color=(254/255.0,212/255.0,85/255.0), label='H4C1')
            box_11 = mpatches.Patch(color=(250/255.0,250/255.0,0), label='H3C5')
            box_12 = mpatches.Patch(color=(255/255.0,255/255.0,87/255.0), label='H3C4')
            box_13 = mpatches.Patch(color=(255/255.0,255/255.0,160/255.0), label='H3C3')
            box_14 = mpatches.Patch(color=(255/255.0,255/255.0,190/255.0), label='H3C2')
            box_15 = mpatches.Patch(color=(255/255.0,255/255.0,255/255.0), label='H3C1')
            box_16 = mpatches.Patch(color=(56/255.0,168/255.0,0), label='H2C5')
            box_17 = mpatches.Patch(color=(76/255.0,230/255.0,0), label='H2C4')
            box_18 = mpatches.Patch(color=(85/255.0,255/255.0,255/255.0), label='H2C3')
            box_19 = mpatches.Patch(color=(163/255.0,255/255.0,115/255.0), label='H2C2')
            box_20 = mpatches.Patch(color=(211/255.0,255/255.0,190/255.0), label='H2C1')
            box_21 = mpatches.Patch(color=(190/255.0,232/255.0,230/255.0), label='H1C5')
            box_22 = mpatches.Patch(color=(115/255.0,223/255.0,255/255.0), label='H1C4')
            box_23 = mpatches.Patch(color=(0,197/255.0,255/255.0), label='H1C3')
            box_24 = mpatches.Patch(color=(0,92/255.0,255/255.0), label='H1C2')
            box_25 = mpatches.Patch(color=(0,38/255.0,115/255.0), label='H1C1')
            plt.legend(handles=[box_1,box_2,box_3,box_4,box_5,box_6,box_7,box_8,box_9,box_10,
                                box_11,box_12,box_13,box_14,box_15,box_16,box_17,box_18,box_19,
                                box_20,box_21,box_22,box_23,box_24,box_25],bbox_to_anchor=(1.2, 1.1))
            imgplot = plt.imshow(list_new_structure)
            plt.savefig(Output_raster_Path_File.get()+'\\'+str(AN)+'_WinSize_'+str(Dim)+'_Graph.png')
            from PIL import Image
            graph = Image.open(Output_raster_Path_File.get()+'\\'+str(AN)+'_WinSize_'+str(Dim)+'_Graph.png')
            graph.show()
            #plt.show()
            #plt.draw()
        # --------------------------------------------------------------------
        self.Button5_15 = tk.Button(self.Labelframe6)
        self.Button5_15.place(relx=0.42, rely=0.267, height=44, width=110
                , bordermode='ignore')
        self.Button5_15.configure(activebackground="#ececec")
        self.Button5_15.configure(activeforeground="#000000")
        self.Button5_15.configure(background="#5badff")
        self.Button5_15.configure(disabledforeground="#a3a3a3")
        self.Button5_15.configure(font="-family {Segoe UI} -size 9 -weight bold")
        self.Button5_15.configure(foreground="#ffffff")
        self.Button5_15.configure(highlightbackground="#d9d9d9")
        self.Button5_15.configure(highlightcolor="black")
        self.Button5_15.configure(pady="0")
        self.Button5_15.configure(text='''Landform Classify''')
        # ------------------------------------------------------------------
        self.Button5_15.configure(command = ShowResult)
        # ------------------------------------------------------------------
if __name__ == '__main__':
    vp_start_gui()





