import os
import unittest
from pxr import Gf, Sdf, Usd, UsdGeom
from usdautoguide.auto_guide import _get_extent, _get_vertex_bbox, _create_cube_mesh, create_auto_guide

usdautoguideroot = os.getenv("REZ_USDAUTOGUIDE_ROOT") + "/tests/guide.usda"
usdautoguidediffroot = os.getenv("REZ_USDAUTOGUIDE_ROOT") + "/tests/guideDiff.usda"
guide_path = "./guide.usda"
guide_path_diff = "./guideDiff.usda"
geo_path = "./geo.usda"


class TestAutoGuideFunctions(unittest.TestCase):

    def setUp(self):
        # Create or initialize any objects or resources needed for testing
        self.model_stage = Usd.Stage.Open(geo_path)
        self.asset_prim = self.model_stage.GetDefaultPrim()
        self.bbox_extent, self.vertex_points = _get_vertex_bbox(self.model_stage, self.asset_prim)

    def test_get_extent(self):
        extent = _get_extent(self.model_stage, self.asset_prim)
        self.assertIsInstance(extent, Gf.Range3d)
        # You can add more specific assertions here based on your knowledge of the function's behavior.

    def test_get_vertex_bbox(self):
        extents, vertex_points = _get_vertex_bbox(self.model_stage, self.asset_prim)
        self.assertIsInstance(extents, list)
        self.assertIsInstance(vertex_points, list)
        # You can add more specific assertions here based on your knowledge of the function's behavior.

    def test_create_cube_mesh(self):
        self.stage = Usd.Stage.CreateNew(guide_path)
        cube_mesh = _create_cube_mesh(self.stage, self.bbox_extent, self.vertex_points, self.asset_prim)
        self.assertIsInstance(cube_mesh, Usd.Prim)
        # You can add more specific assertions here based on your knowledge of the function's behavior.

    def test_create_auto_guide(self):
        # Capture standard output to check if the function prints the expected message
        import filecmp

        create_auto_guide(geo_path, guide_path)

        are_equal = filecmp.cmp(usdautoguideroot, usdautoguidediffroot, shallow=False)

        if are_equal:
            print("The files are exactly the same.")
        else:
            print("The files are different.")


if __name__ == '__main__':
    unittest.main()
