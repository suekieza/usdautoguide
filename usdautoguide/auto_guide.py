from pxr import Gf, Sdf, Usd, UsdGeom
from typing import Union
from pathlib import Path



def _get_extent(stage: Usd.Stage, prim: Union[str, Usd.Prim]) -> Gf.Range3d:
    """
    Calculates & sets the extents of a prim based on its World Bounds

    Args:
        stage (Usd.Stage):           An opened stage file via Usd.Stage.Open().
        prim (str or Usd.Prim):      The address to the primitive such as '/assetname'
                                     or the prim object itself.

    Returns:
        Gf.Range3d:                  Axis-aligned, object-space extent.

    Raises:
        ValueError:                  If an error occurs while computing the extent.
    """

    # Convert prim_path string to prim if it's a string
    if isinstance(prim, str):
        prim_path = prim
        prim = stage.GetPrimAtPath(prim_path)

    try:
        # Create a BBoxCache to compute the world bounds
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                       includedPurposes=[UsdGeom.Tokens.default_,
                                                         UsdGeom.Tokens.render],
                                       useExtentsHint=False,
                                       ignoreVisibility=False)

        bbox_bounds = bbox_cache.ComputeWorldBound(prim)
        bound_align = bbox_bounds.ComputeAlignedBox()
        return bound_align

    except Exception as e:
        raise ValueError(f"Error in get_extent: {str(e)}")


def _get_vertex_bbox(stage: Usd.Stage, prim: Union[str, Usd.Prim]) -> tuple[Gf.Range3d, list[Gf.Vec3d]]:
    """
    Calculates the vertex bounding box (bbox) of a USD stage or prim.

    Args:
        stage (Usd.Stage):           An opened stage file via Usd.Stage.Open().
        prim (str or Usd.Prim):      The address to the primitive such as '/root/cube_model'
                                     or the prim object itself.

    Returns:
        Tuple[Gf.Range3d, List[Gf.Vec3d]]: A tuple containing the axis-aligned, object-space extent
        (Gf.Range3d) and a list of vertex points (List[Gf.Vec3d]) for the bounding box.

    Raises:
        ValueError:                  If an error occurs while computing the extent.
    """
    try:
        # Calculate the extent using the get_extent function
        bound_align = _get_extent(stage, prim)
        bbox_min = bound_align.GetMin()
        bbox_max = bound_align.GetMax()

        def convert_to_float(number):
            # Function to convert numbers in scientific notation to float
            if "e" in str(number):
                string_min = str(number)
                correction = string_min.split("e")
                return float(correction[0])
            return number

        # Correct and convert the min and max values to float
        corrected_min = [convert_to_float(number) for number in bbox_min]
        corrected_max = [convert_to_float(number) for number in bbox_max]

        extents = [
            corrected_min,
            corrected_max
        ]

    except Exception as e:
        raise ValueError(f"Error in get_vertex_bbox when extracting extents: {str(e)}")

    try:
        # Define vertex points of the bounding box
        vertex_points = [
            Gf.Vec3d(corrected_max[0], corrected_min[1], corrected_max[2]),
            Gf.Vec3d(corrected_min[0], corrected_min[1], corrected_max[2]),
            Gf.Vec3d(corrected_max[0], corrected_max[1], corrected_max[2]),
            Gf.Vec3d(corrected_min[0], corrected_max[1], corrected_max[2]),
            Gf.Vec3d(corrected_min[0], corrected_min[1], corrected_min[2]),
            Gf.Vec3d(corrected_max[0], corrected_min[1], corrected_min[2]),
            Gf.Vec3d(corrected_min[0], corrected_max[1], corrected_min[2]),
            Gf.Vec3d(corrected_max[0], corrected_max[1], corrected_min[2]),
        ]
        return extents, vertex_points

    except Exception as e:
        raise ValueError(f"Error in get_vertex_bbox when defining vertex_points : {str(e)}")


def _create_cube_mesh(stage: Usd.Stage, bbox_extent: Gf.Range3d,
                      vertex_points: list[Gf.Vec3d], default_prim: Union[str, Usd.Prim]) -> Usd.Prim:
    """
    Creates a cube mesh in USD stage with given parameters.

    Args:
        stage (Usd.Stage):           The USD stage where the cube mesh will be created.
        bbox_extent (Gf.Range3d):    Axis-aligned, object-space extent of the cube.
        vertex_points (list):        List of vertex points for the cube.
        default_prim (Usd.Prim):     The default primitive in the stage.

    Returns:
        Usd.Prim:                    The created cube mesh.

    Raises:
        ValueError:                  If an error occurs while creating the cube mesh.
    """
    try:
        # Create necessary prims for the cube mesh
        asset_prim = stage.DefinePrim(f"{default_prim.GetPath()}", "Xform")
        model_prim = stage.DefinePrim(f"{default_prim.GetPath()}/model", "Xform")
        guide_prim = stage.DefinePrim(f"{default_prim.GetPath()}/model/guide", "Xform")
        cube_mesh = stage.DefinePrim(f"{default_prim.GetPath()}/model/guide/box", "Mesh")

        # Set face vertex counts
        face_vertex_counts_attribute = cube_mesh.CreateAttribute("faceVertexCounts", Sdf.ValueTypeNames.Int)
        face_vertex_counts_attribute.Set([4, 4, 4, 4, 4, 4])

        # Set vertex points
        points_attribute = cube_mesh.CreateAttribute("points", Sdf.ValueTypeNames.Point3f)
        points_attribute.Set(vertex_points)

        # Set extent
        extents_cube = cube_mesh.CreateAttribute("extent", Sdf.ValueTypeNames.Vector3fArray)
        extents_cube.Set(bbox_extent)

        # Set face vertex indices
        face_vertex_indices_attribute = cube_mesh.CreateAttribute("faceVertexIndices", Sdf.ValueTypeNames.Int)
        face_vertex_indices_attribute.Set([0, 1, 3, 2, 4, 5, 7, 6, 6, 7, 2, 3, 5, 4, 1, 0, 5, 0, 2, 7, 1, 4, 6, 3])

        return cube_mesh

    except Exception as e:
        raise ValueError(f"Error in create_cube_mesh: {str(e)}")


def create_auto_guide(geo_path: str, guide_path: str):
    """
    Creates an auto guide for a model in USD stage.

    Args:
        geo_path (str):    Path to the geo USD file.
        guide_path (str):    Path where the guide will be saved.

    Raises:
        ValueError:          If an error occurs while creating the auto guide.
    """
    # Open the geo stage
    if not Path(geo_path).exists():
        raise FileNotFoundError(f"The file: {geo_path} does not exist.")

    try:
        model_stage = Usd.Stage.Open(geo_path)

        # Get default Prim
        asset_prim = model_stage.GetDefaultPrim()
        print(f"Auto Guide will be calculated for: {asset_prim.GetPath()}")

        # Calculate bounding box extent and vertex points
        bbox_extent, vertex_points = _get_vertex_bbox(model_stage, asset_prim)

        # Create a new USD stage for the guide and create the cube mesh
        stage = Usd.Stage.CreateNew(guide_path)
        _create_cube_mesh(stage, bbox_extent, vertex_points, asset_prim)

        # Save the guide stage
        stage.Save()

    except Exception as e:
        raise ValueError(f"Error in create_auto_guide: {str(e)}")
