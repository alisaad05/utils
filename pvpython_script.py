#TODO: replace directory strings by r strings so that "\" works instead of "\\"
#TODO: Write wrapper class to hide the VTU processing, custom colors and color presets (in a similar way as vtktools)
docstring= """ 
************************* Ali SAAD 2014 ***************************

* VTU/PVSM (paraview state) to PNG Utility 
  + Crop .....................(needs ImageMagick.exe) 
  + Animation Creator ........(needs mencoder.exe)

* Paraview offscreen script that exports PNG images from simulation
  results in a seamless and fast way (faster than using GUI). This
  is extremely useful for heavy 3D simulations wth big data and la-
  rge mesh, where Paraview may crash, especially if rendering LateX

* Supports selective data loading, i.e. user can specify the fields
  to process instead of loading all data from the VTU file

* Use with pvpython.exe version 4.2 located in the "bin" folder 
  of Paraview installation (mainly for the .tex rendering and com-
  patibility of some functions e.g. SaveScreenshot)

*******************************************************************
"""
print docstring


# INPUT OPTIONS (paths, options ...)
# ==============================

dirname =  r"U:\Intel_Cluster_Cases\5_SMACS_LS"
foldername = r"B8_boussinesq"  # A_retrait # B5_boussinesq
vtu_name = "out_thermique_"

scalar_to_export = 'Vitesse'  # FractionPair # Vitesse # Pression
min_value = 0.0
max_value = 1e-3

SHOW_CENTER_AXIS = False
SHOW_ORIENTATION_AXIS = True

# OUTPUT OPTIONS (DISABLE ALL IF RUNNING IN PARAVIEW'S PYTHON SHELL)
# ====================================================================
SHOW_TIME = 	True	# True # False
EXPORT_PNG = 	True	# True # False
CROP_PNG = 		True	# True # False
MAKE_ANIMATION=	True	# True # False
OFFSCREEN_RENDERING = True
fps=10
LOW = [800,600]
HIGH = [1280,1024]
RESOLUTION = HIGH # LOW #  HIGH

# ==========================================================================================================================

P0_fields_list = []
#TODO: when the class pvtools will be created, check the number of scalar in this list and create a LUT for each one
P1_fields_list = [scalar_to_export, "d_interface_filtered", "d_interface"]

#CUSTOM COLORS
# ============
RED = [1,0,0]
BLUE = [0,0,1]
BLACK = [0,0,0]

# PRESETS (painfully defined by hand :))
# ========
BlueToRedRainbow = [0.0, 0,0,1, 
                    1.0, 1,0,0]
RainbowDesaturated = [  0.0	 ,	0.28, 		0.28, 		0.86, 
						0.143, 	0.0,		0.0, 		0.36, 
						0.285, 	0.0,		1.0, 		1.0, 
						0.429, 	0.0,		0.5, 		0.0, 
						0.571, 	1.0,		1.0, 		0.0, 
						0.714, 	1.0,		0.38, 		0.0, 
						0.857, 	0.42,		0.0, 		0.0, 
						1.0, 	0.88,		0.3, 		0.3 ]
RainbowBlendedWhite = [ 0.0	 ,	1,1,1, 
						0.17, 	0,0,1,
						0.34, 	0,1,1, 
						0.5, 	0,1,0,
						0.67, 	1,1,0,
						0.84, 	1,0,0,
						1.0, 	0.88, 0, 1 ]
						
"""
Update views, isometric and other routines inpired by MAYAVI's tvtk_scene.py
"""
def update_view(VIEW, position, viewup, focalpoint = [0,0,0]): #x,y,z, vx,vy,vz):
	VIEW.CameraPosition = position# [x,y,z]
	VIEW.CameraViewUp = viewup#[vx,vy,vz]
	VIEW.CameraFocalPoint = focalpoint

def Z_plus_view(VIEW):
	position = 	[0,0,1]
	viewup = 	[0,1,0]
	update_view(VIEW, position, viewup)
	
def isometric_view(VIEW):
	position = 	[1,1,1]
	viewup = 	[0,0,1]
	update_view(VIEW, position, viewup)
	
def custom_view(VIEW):
	# VIEW.InteractionMode = '2D'
	VIEW.CameraParallelScale = 0.06
	# VIEW.CameraClippingRange = [0.1, 0.1]
	position = 		[0.08, 0.03, 0.25]
	focalpoint = 	[0.08, 0.03, 0.0]
	viewup = [0,1,0]
	update_view(VIEW, position, viewup, focalpoint)
	
	
import subprocess
import os

if EXPORT_PNG: 
	from paraview.simple import *

	# START FROM STATE FILE
	# =======================
	""" The drawback with state files is that they depend on a result path that cannot be changed easily from the outside"""
	# statefile = dirname + foldername + "pv.pvsm"
	# servermanager.LoadState(statefile) #SaveState
	# reader  = FindSource("out_thermique_0*")

	# START FROM VTU FILES
	# =====================
	print("\nREADING VTU...")
	filedir = dirname + "\\" + foldername + "\\" + "resultatsVTU\\"
	
	# ----  DEPRECATED FILE INPUT ---- 
	# Time options to determine the correct VTU file names
	# t_start=0
	# t_end=80
	# frequency_VTU=1
	# filenamelist = [filedir + vtu_name + str(i).rjust(5,'0')+'.vtu' for i in range(t_start,t_end,frequency_VTU)] #I f***ing love python generators and list comprehension !!!
	# Make sure files exist (make sure user has not given wrong t_start or t_end parameters)
	# for f in filenamelist: 
		# if not os.path.isfile(f): 
			# raise Exception("\n\nFile " + f + " does not exist ... ! \nCheck the values of t_start, t_end and frequency_VTU\n\n" )
	# ------------------------------
	filenamelist = os.listdir(filedir)
	filepathlist = [ filedir + name for name in filenamelist ]
	reader = XMLUnstructuredGridReader( FileName= filepathlist )

	# P1 FIELDS
	reader.PointArrayStatus = P1_fields_list
	# P0 FIELDS
	reader.CellArrayStatus = P0_fields_list
	# Activate the "eye" icon next to the source
	Show() 
	# Read the time array
	timesteps = reader.TimestepValues
	# Misc
	data_representation = GetDisplayProperties(reader)

	# CONTROL CAMERA
	# ================
	view = GetRenderView()
	view.ResetCamera()
	SetActiveView(view)
	view.ViewSize= RESOLUTION
	view.Background = [1,1,1]  #white
	view.CenterAxesVisibility = int(SHOW_CENTER_AXIS)
	view.OrientationAxesVisibility = int(SHOW_ORIENTATION_AXIS)
	view.OrientationAxesLabelColor = BLUE
	#Offscreen rendering to be specified before calling the first Render()
	view.UseOffscreenRendering= int(OFFSCREEN_RENDERING)
	view.UseOffscreenRenderingForScreenshots= int(OFFSCREEN_RENDERING)
	custom_view(view) # Z_plus_view # custom_view
	Render()

	# SHOW TIME ANNOTATION
	# ======================
	if SHOW_TIME :
		annTime = AnnotateTimeFilter(reader)
		annTime.Format = '$Time: \\hspace{1} %1.0f \\hspace{1} sec$'
		annTimeDisplay = GetDisplayProperties(annTime, view=view)
		annTimeDisplay.FontFamily= 'Arial' # Arial # Times # Courier
		annTimeDisplay.FontSize= 10
		annTimeDisplay.Color= BLACK # BLUE
		annTimeDisplay.Opacity= 1.0
		annTimeDisplay.Bold=0
		annTimeDisplay.Italic=0
		annTimeDisplay.Shadow=0
		
		# annTimeDisplay.WindowLocation= "LowerLeftCorner"  # Upper/Lower + Left/Right + Corner , e.g. "LowerRightCorner" # or LowerCenter/UpperCenter # or "AnyLocation"
		annTimeDisplay.Position = [0.04, 0.22]
		Show(annTime)

	# DISPLAY VELOCITY FIELD (ONLY FOR VTU, DO NOT USE FOR STATE FILES)
	# =================================================================
	# SHOW SCALAR OR VECTOR
	
	Scalar_LUT = GetLookupTableForArray( scalar_to_export, 3, 
											Discretize=0, 
											RGBPoints= RainbowBlendedWhite ,   # BlueToRedRainbow (HSV) # RainbowDesaturated (HSV) # RainbowBlendedWhite (RGB)
											VectorMode='Magnitude', 
											# NanColor=[0.498039215686275, 0.498039215686275, 0.498039215686275], 
											ColorSpace='RGB', # RGB # HSV # Lab # Diverging
											ScalarRangeInitialized=1.0, 
											AllowDuplicateScalars=1 
										)

	data_representation.ColorArrayName = scalar_to_export
	data_representation.LookupTable = Scalar_LUT

	Scalar_LUT.RescaleTransferFunction(min_value, max_value)
	Scalar_LUT.LockScalarRange = 1
	
	Scalar_LUT.Discretize = 1
	Scalar_LUT.NumberOfTableValues = 50
	# Scalar_LUT.ColorSpace='RGB' # RGB # HSV # Lab # Diverging
	Render()

	# SHOW CORRESPONDING SCALAR BAR
	ScalarBar = CreateScalarBar()
	ScalarBar = GetScalarBar(Scalar_LUT, view)
	ScalarBar.Position = [0.75, 0.3] # this is position
	ScalarBar.Position2 = [0.2, 0.35] # this is size
	ScalarBar.Orientation = 'Vertical' # Horizontal # Vertical
	ScalarBar.Title = scalar_to_export
	ScalarBar.TitleBold = 0
	ScalarBar.TitleItalic = 0
	ScalarBar.TitleOpacity = 1.0
	ScalarBar.TitleFontFamily = 'Arial'
	ScalarBar.TitleShadow = 0
	ScalarBar.TitleJustification = 'Centered' # Centered # Left s# Right
	ScalarBar.ComponentTitle = '[m/s]'
	ScalarBar.TitleColor = BLUE
	ScalarBar.TitleFontSize = 12
	ScalarBar.AspectRatio = 12 #25
	# ScalarBar.TextPosition = 'Ticks left/bottom, annotations right/top'
	ScalarBar.TextPosition = 'Ticks right/top, annotations left/bottom'

	ScalarBar.LabelBold = 0
	ScalarBar.LabelItalic = 0
	ScalarBar.LabelOpacity = 0
	ScalarBar.LabelShadow = 0
	ScalarBar.LabelColor = RED
	ScalarBar.LabelFontSize = 10
	ScalarBar.LabelOpacity = 1.0
	ScalarBar.LabelFontFamily = 'Arial'
	ScalarBar.NumberOfLabels = 0
	ScalarBar.DrawTickMarks = 0
	ScalarBar.DrawTickLabels = 0
	ScalarBar.AddRangeAnnotations = 1 # min and max on scalarbar
	ScalarBar.DrawNanAnnotation = 0
	ScalarBar.NanAnnotation = 'NaN'

	ScalarBar.AutomaticLabelFormat = 0
	ScalarBar.LabelFormat = '%-#2.2E'
	ScalarBar.RangeLabelFormat = '%2.4e'
						 
	GetRenderView().Representations.append(ScalarBar)
	ScalarBar.LookupTable = Scalar_LUT
	print("\nFinished Processing VTU files'")

	# DRAW FILTERED LS CONTOUR
	ContourLS = Contour(Input= reader)
	ContourLS_Display = Show(ContourLS, view)
	ColorBy(ContourLS_Display, None)
	ContourLS.PointMergeMethod = 'Uniform Binning'
	ContourLS.ContourBy = ['POINTS', 'd_interface_filtered']
	ContourLS.Isosurfaces = [0.0]
	ContourLS_Display.LineWidth = 3.0 
	ContourLS_Display.DiffuseColor = BLACK 
	Render()
	
	# DRAW INITIAL LS CONTOUR
	ContourLS2 = Contour(Input= reader)
	ContourLS2_Display = Show(ContourLS2, view)
	ColorBy(ContourLS2_Display, None)
	ContourLS2.PointMergeMethod = 'Uniform Binning'
	ContourLS2.ContourBy = ['POINTS', 'd_interface']
	ContourLS2.Isosurfaces = [0.0]
	ContourLS2_Display.LineWidth = 1.0 
	ContourLS2_Display.DiffuseColor = RED 
	Render()
	
# LOOP OVER FILES AND EXPORT PNG
# ================================
img_dir = dirname + "\\" + foldername + "\\" + "img\\"

if EXPORT_PNG :
	print("\n\nEXPORTING ...\n")
	if not os.path.exists(img_dir):
		os.makedirs(img_dir)
	
	for t in timesteps:
		# if t > 4: break
		view.ViewTime = t	
		custom_view(view)
		# data_representation.RescaleTransferFunctionToDataRange()
		Render() 
		
		imgname = "Frame_" + str(t)[:-2].rjust(5,'0') + ".png"
		filename = img_dir + imgname
		# [:-2] strips the deicmal part coming from paraview's timestep
		# rjust(5,'0') returns a new string with leading zeros 
		# LEADING ZEROS ARE CRUCIAL FOR THE SORTING ALGORITHM USED DURING FILE LISTING (Dir) BEFORE ANIMATION
		
		# EXPORT PNG METHODS
		# ==================
		""" METHOD 1: works all versions, basic options"""
		# WriteImage(filename, Magnification= 1)
		
		# aLayout = GetLayout()
		""" METHOD 2: works only with Paraview 4.2 and above: allows more options and control """
		SaveScreenshot(filename, layout=None, magnification=1, quality=1)
		print(imgname + " was successfully exported")
		
		""" METHOD 3: http://www.paraview.org/ParaView3/Doc/Nightly/www/py-doc/paraview.simple.html#paraview.simple.WriteAnimation"""
		# WriteAnimation(	filename, 
						# Magnification=1, 
						# FrameRate=1.0, 
						# Compression=True, 
						# Quality=2,
						# BackgroundColor = (1.0,1.0,1.0)
						# )
	print("\nFinished exporting PNG files from VTU files")


if CROP_PNG :
	print("\n\nCROPPING ...")
	if not os.path.exists(img_dir):
		raise Exception("\nThe directory '" + img_dir + "' does not exist !")
	command = ('mogrify',
			   "-format",
			   "png",
			   "-trim",
			   img_dir+'*.png'
			   )
	subprocess.call(command)		   
	print("\nFinished cropping PNG files")

	
if MAKE_ANIMATION :	
	print("\n\nCREATING ANIMATION ...")
	if not os.path.exists(img_dir):
		raise Exception("\nThe directory '" + img_dir + "' does not exist !")
	os.chdir(img_dir)
	subprocess.call('dir /b /o *.png > files.txt', shell=True)	
	
	animationname = dirname + "\\Animation_" + foldername.lower() + "_" + scalar_to_export + "_" + str(fps) + "fps.avi"
	command = ('mencoder',
			   'mf://@files.txt', #works only in the current dir
			   '-mf',
			   'type=png:fps='+str(fps),
			   '-ovc',
			   'lavc',
			   '-lavcopts',
			   'vcodec=mpeg4',
			   '-oac',
			   'copy',
			   '-o',
			   animationname )   
	subprocess.call(command)	
	
	os.chdir(dirname)	
	print("\n\n\nANIMATION.avi was created from PNG files")
		   
	   