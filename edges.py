"""
#########################################################################################################################
# Bc. Veronika Hajdúchová, 2023                                                                                         #
#                                                                                                                       #
# Diplomová práca: Detekcia hrán na lidarových dátach pomocou decimácie trojuholníkovej siete.                          #
# Univerzita Komenského v Bratislave, Prírodovedecká fakulta, Katedra fyzickej geografie a geoinformatiky               #
#                                                                                                                       #
# Master thesis: Edge detection on lidar data using triangular network decimation                                       #
# Comenius University Bratislava, Faculty of Natural Sciences, Department of Physical Geography and Geoinformatics      #
#                                                                                                                       #
#########################################################################################################################
"""

import trimesh
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
import ezdxf
import sys
import time
import os

def angle_between_faces(mesh, face1, face2):
    try:
        normal1 = mesh.face_normals[face1]
        normal2 = mesh.face_normals[face2]
        dot_product = np.dot(normal1, normal2)
        dot_product = np.clip(dot_product, -1.0, 1.0)
        angle_rad = np.arccos(dot_product)
        angle_deg = np.degrees(angle_rad)
        return angle_deg
    except Exception as e:
        print(f"Error calculating angle between faces {face1} and {face2}: {e}")
        return 0

def remove_duplicates(mesh):
    try:
        #remove duplicate vertices
        mesh.merge_vertices()

        #remove duplicate faces
        unique_faces = mesh.unique_faces()
        mesh.update_faces(unique_faces)
    except Exception as e:
        print(f"Error removing duplicates: {e}")

    return mesh

def main(input, output_shp, threshold_angle, crs="EPSG:5514", output_obj=None, output_dxf=None):
    if not os.path.exists(input):
        print(f"Input file {input} does not exist.")
        return

    try:
        #load mesh
        mesh = trimesh.load(input)
    except Exception as e:
        print(f"Error loading mesh from file {input}: {e}")
        return

    if not hasattr(mesh, 'faces') or not hasattr(mesh, 'face_normals'):
        print("Invalid mesh data. Ensure the input file contains a valid 3D mesh.")
        return

    print(f"Loaded {len(mesh.vertices)} vertices and {len(mesh.faces)} faces.")

    mesh = remove_duplicates(mesh)

    print(f"After removing duplicates: {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")

    try:
        #compute face adjacency
        adjacency = mesh.face_adjacency
    except Exception as e:
        print(f"Error computing face adjacency: {e}")
        return

    selected_faces = set()
    shared_edges = []

    #process each pair of adjacent faces
    for face1, face2 in adjacency:
        angle = angle_between_faces(mesh, face1, face2)
        if angle > threshold_angle:
            selected_faces.add(face1)
            selected_faces.add(face2)
            shared_edge = np.intersect1d(mesh.faces[face1], mesh.faces[face2])
            if len(shared_edge) == 2:
                shared_edges.append(shared_edge)

    if not shared_edges:
        print("No shared edges found between selected faces.")
        return

    print(f"Selected {len(selected_faces)} faces.")
    
    mask = np.zeros(len(mesh.faces), dtype=bool)
    mask[list(selected_faces)] = True
    selected_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[mask])

    #shp export
    try:
        shared_edges_vertices = np.unique(np.concatenate(shared_edges))
        lines = [LineString(mesh.vertices[shared_edge]) for shared_edge in shared_edges]
        gdf = gpd.GeoDataFrame(geometry=lines, crs=crs)
        gdf.to_file(output_shp)
    except Exception as e:
        print(f"Error exporting to Shapefile {output_shp}: {e}")

    #obj export
    if output_obj:
        try:
            selected_mesh.export(output_obj)
        except Exception as e:
            print(f"Error exporting selected faces to {output_obj}: {e}")

    #dxf export
    if output_dxf:
        try:
            doc = ezdxf.new()
            msp = doc.modelspace()
            for shared_edge in shared_edges:
                points = [mesh.vertices[vertex] for vertex in shared_edge]
                msp.add_polyline3d(points)
            doc.saveas(output_dxf)
        except Exception as e:
            print(f"Error exporting to DXF file {output_dxf}: {e}")

    #check outputs
    output_files = [output_shp]
    if output_obj:
        output_files.append(output_obj)
    if output_dxf:
        output_files.append(output_dxf)
    
    all_files_created = all(os.path.exists(file) for file in output_files)
    if all_files_created:
        print("All output files were created successfully.")
    else:
        print("Some output files were not created successfully.")

if __name__ == "__main__":
    print("Script started at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    if len(sys.argv) < 4:
        print("Usage: python edge.py input output_shp threshold_angle [crs] [output_obj] [output_dxf]")
        sys.exit(1)

    input = sys.argv[1]
    output_shp = sys.argv[2]

    try:
        threshold_angle = float(sys.argv[3])
    except ValueError:
        print("Angle threshold must be a valid number.")
        sys.exit(1)

    if not (0 <= threshold_angle <= 180):
        print("Angle threshold must be between 0 and 180 degrees.")
        sys.exit(1)

    crs = sys.argv[4] if len(sys.argv) >= 5 else "EPSG:5514"
    output_obj = sys.argv[5] if len(sys.argv) >= 6 else None
    output_dxf = sys.argv[6] if len(sys.argv) >= 7 else None
    

    main(input, output_shp, threshold_angle, crs, output_obj, output_dxf)

    end_time = time.time()
    print(f"Script took {end_time - start_time:.2f} seconds to run.")
