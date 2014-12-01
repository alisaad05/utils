""" 
Ali SAAD 2014
Paraview offscreen script that exports PNG images from simulation results
For best rendering results use with pvpython.exe version 4.2 (mainly for the .tex rendering)
"""
# PATHS
# =====
foldername = "A_retrait\\"
filename = "out_thermique_"
dirname =  "C:\\Users\\RASPI\\Google Drive\\WORK Shared Folder\\Python Paraview Offscreen\\Open result and animate\\"

#CUSTOM OPTIONS 
# ============
SHOW_TIME = 	False	# True # False
EXPORT_PNG = 	True	# True # False
CROP_PNG = 		True	# True # False
MAKE_ANIMATION=	False	# True # False
fps=5

#CUSTOM COLORS
# ============
RED = [1,0,0]
BLUE = [0,0,1]
BLACK = [0,0,0]

"""
Update views, isometric and other routines inpired by MAYAVI's tvtk_scene.py
"""
def update_view(VIEW, position, viewup, focalpoint = [0,0,0]): #x,y,z, vx,vy,vz):
	VIEW.CameraPosition = position# [x,y,z]
	VIEW.CameraViewUp = viewup#[vx,vy,vz]
	VIEW.CameraFocalPoint = focalpoint

def Z_plus_view(VIEW):
	position = [0,0,1]
	viewup = [0,1,0]
	update_view(VIEW, position, viewup)
	
def isometric_view(VIEW):
	position = [1,1,1]
	viewup = [0,0,1]
	update_view(VIEW, position, viewup)
	
def custom_view(VIEW):
	# VIEW.InteractionMode = '2D'
	VIEW.CameraParallelScale = 0.06
	# VIEW.CameraClippingRange = [0.1, 0.1]
	position = 		[0.08, 0.03, 0.25]
	focalpoint = 	[0.08, 0.03, 0.0]
	viewup = [0,1,0]
	update_view(VIEW, position, viewup, focalpoint)
	
	
from paraview.simple import *
import subprocess
import os

# START FROM STATE FILE
# =======================
""" The drawback with state files is that they depend on a result path that cannot be changed easily from the outside"""
# statefile = dirname + foldername + "pv.pvsm"
# servermanager.LoadState(statefile) #SaveState
# reader  = FindSource("out_thermique_0*")

# START FROM VTU FILES
# =====================
print("\n\nREADING VTU...")
dir = dirname + foldername + "resultatsVTU\\" + filename
reader = XMLUnstructuredGridReader( FileName= [dir+str(i).rjust(5,'0')+'.vtu' for i in range(0,40,10)]) #I fucking love python generators and list comprehension !!!
# P1 FIELDS
reader.PointArrayStatus = ['d_interface', 'd_interface_filtered','Vitesse']
# P0 FIELDS
reader.CellArrayStatus = ['Heaviside_M_p0']
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
view.ViewSize=[1280,1024] #[1280,1024]
view.Background = [1,1,1]  #white
view.CenterAxesVisibility = 0
view.OrientationAxesVisibility = 0
view.OrientationAxesLabelColor = BLUE
#Offscreen rendering to be specified before calling the first Render()
view.UseOffscreenRendering=1
view.UseOffscreenRenderingForScreenshots=1
custom_view(view) # Z_plus_view # custom_view
Render()

# SHOW TIME ANNOTATION
# ======================
if SHOW_TIME is True:
	annTime = AnnotateTimeFilter(reader)
	annTimeDisplay = GetDisplayProperties(annTime, view=view)
	annTimeDisplay.Color= RED
	annTimeDisplay.Bold=1
	Show(annTime)

# DISPLAY VELOCITY FIELD (ONLY FOR VTU, DO NOT USE FOR STATE FILES)
# =================================================================
# SHOW SCALAR OR VECTOR
min = 0.0
max = 1.6e-10
Vitesse_LUT = GetLookupTableForArray( "Vitesse", 3, 
										Discretize=0, 
										# RGBPoints=[min, 0.0, 0.0, 1.0, max, 1.0, 0.0, 0.0], 
										VectorMode='Magnitude', 
										# NanColor=[0.498039215686275, 0.498039215686275, 0.498039215686275], 
										 
										ScalarRangeInitialized=1.0, 
										AllowDuplicateScalars=1 
									)

data_representation.ColorArrayName = 'Vitesse'
data_representation.LookupTable = Vitesse_LUT

Vitesse_LUT.RescaleTransferFunction(min,max)
Vitesse_LUT.LockScalarRange = 0
Vitesse_LUT.Discretize = 0
Vitesse_LUT.NumberOfTableValues = 20
Vitesse_LUT.ColorSpace='HSV' # RGB # HSV # Lab # Diverging

Render()

# SHOW CORRESPONDING SCALAR BAR
ScalarBar = CreateScalarBar()
# ScalarBar = CreateScalarBar()
ScalarBar = GetScalarBar(Vitesse_LUT, view)
ScalarBar.Position = [0.75, 0.3] # this is position
ScalarBar.Position2 = [0.2, 0.35] # this is size
ScalarBar.Orientation = 'Vertical' # Horizontal # Vertical
ScalarBar.Title = '$\\langle v^F \\rangle$'
ScalarBar.TitleBold = 0
ScalarBar.TitleItalic = 0
ScalarBar.TitleJustification = 'Centered' # Centered # Left s# Right
ScalarBar.ComponentTitle = '[m/s]'
ScalarBar.TitleColor = BLUE
ScalarBar.TitleFontSize = 15
ScalarBar.DrawTickMarks = 0
ScalarBar.AddRangeAnnotations = 1
ScalarBar.AspectRatio = 15 #25
# ScalarBar.TextPosition = 'Ticks left/bottom, annotations right/top'
ScalarBar.TextPosition = 'Ticks right/top, annotations left/bottom'

ScalarBar.LabelBold = 0
ScalarBar.LabelItalic = 0
ScalarBar.LabelColor = RED
ScalarBar.LabelFontSize = 10
ScalarBar.AutomaticLabelFormat = 0
ScalarBar.DrawTickLabels = 0
ScalarBar.LabelFormat = '%-#2.4E'
ScalarBar.RangeLabelFormat = '%2.2E'
					 
GetRenderView().Representations.append(ScalarBar)
ScalarBar.LookupTable = Vitesse_LUT
print("\nFinished Processing VTU files'")

# LOOP OVER FILES AND EXPORT PNG
# ================================
if EXPORT_PNG is True:
	print("\n\nEXPORTING ...")
	if not os.path.exists(dirname + foldername + 'img'):
		os.makedirs(dirname + foldername + 'img')
	
	for t in timesteps:
		# if t > 4: break
		view.ViewTime = t	
		custom_view(view)
		data_representation.RescaleTransferFunctionToDataRange(True)
		Render() 
		
		filename = dirname + foldername + "img\\" + "Frame " + str(t)+ ".png"
		# filename = "Frame " + str(t)+ ".png"
		
		# EXPORT PNG METHODS
		# ==================
		""" METHOD 1: works all versions, basic options"""
		# WriteImage(filename, Magnification= 1)
		
		# aLayout = GetLayout()
		""" METHOD 2: works only with Paraview 4.2 and above: allows more options and control """
		SaveScreenshot(filename, layout=None, magnification=1, quality=1)
		print("'Frame " + str(t)+ ".png' was successfully exported")
		
		""" METHOD 3: http://www.paraview.org/ParaView3/Doc/Nightly/www/py-doc/paraview.simple.html#paraview.simple.WriteAnimation"""
		# WriteAnimation(	filename, 
						# Magnification=1, 
						# FrameRate=1.0, 
						# Compression=True, 
						# Quality=2,
						# BackgroundColor = (1.0,1.0,1.0)
						# )
print("\nFinished exporting PNG files from VTU files")


if CROP_PNG is True:
	print("\n\nCROPPING ...")
	command = ('mogrify',
			   "-format",
			   "png",
			   "-trim",
			   dirname + foldername + 'img\\*.png'
			   )
	subprocess.check_call(command)		   
	print("\nFinished cropping PNG files")

	
if MAKE_ANIMATION is True:	
	print("\n\nCREATING ANIMATION ...")
	command = ('mencoder',
			   'mf://'+ dirname + foldername + 'img\\*.png',
			   '-mf',
			   'type=png:fps='+str(fps),
			   '-ovc',
			   'lavc',
			   '-lavcopts',
			   'vcodec=mpeg4',
			   '-oac',
			   'copy',
			   '-o',
			   'ANIMATION.avi')		   
	subprocess.check_call(command)		   
	print("\nANIMATION.avi was created from PNG files")
		   
		   
		   
		   