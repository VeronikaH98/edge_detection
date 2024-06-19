# Extract the edges
Extract the sharp edges from the triangular mesh file.

The script uses Trimesh library to load a 3D mesh from an input file and checks for duplicates, cleans mesh by removing duplicate vertices and faces and prints the number of vertices and triangles in the loaded mesh before and after cleaning. Then it identifies pairs of adjacent triangles (faces) and for each pair computes the angle between their normal using the dot product of the face normals to find cosine of the angle and converts it to degrees. If the angle exceeds the specifies threshold (threshold_angle) both faces are added to a set of selected faces and shared edges between those faces are identified and stored in list. The main result is shapefile with selected shared edges and if specifies, the script exports the selected faces as .obj or shared edges as .dxf. 

To run this script, you must define in the command line: input output threshold_angle

  + input = input file containing 3D mesh
  + output_shp = file name for selected edges 
  + threshold_angle = angle threshold for edge detection in degrees
  + crs = coordinate reference system for the shapefile, defaults to EPSG:5514 (optional)
  + output_obj = file name for selected triangles (optional)
  + output_dxf = file name for selected edges (optional)

<br />

	python edges.py input output_shp threshold_angle [crs] [output_obj] [output_dxf]

	e.g.: python edges.py dem.obj edges.shp 30
          python edges.py dem.obj edges.shp 30 4326 faces.obj edges.dxf

Required libraries are Trimesh, Numpy, Geopandas, Ezdxf, Sys* and Time*.
		
    pip install trimesh
    pip install numpy
    pip install geopandas
    pip install ezdxf
		
*library is built-in with python, no need to install, just import it
