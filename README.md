# Auto Guide Generator

This Python script is designed to generate an auto guide for a 3D model in USD (Universal Scene Description) format. The guide is represented as a cube mesh that encompasses the bounding box of the input 3D model. This README provides information on the prerequisites for running the script and how to use it effectively.

## Prerequisites

Before using this script, you need to ensure that you have the following prerequisites installed:

- **Pixar's USD (Universal Scene Description)**: You must have Pixar's USD library and Python bindings installed. You can find more information about USD installation [here](https://github.com/PixarAnimationStudios/USD).


## Usage

To use this script, follow these steps:

1. Import the required modules at the beginning of your Python script:

    ```python
    from usdautoguide.auto_guide import create_auto_guide
    ```

2. Define the paths to your input 3D model (model_geo_path) and the desired output location for the auto guide (guide_path).

3. Call the `create_auto_guide` function, passing the model path and guide path as arguments:

    ```python
    create_auto_guide(model_geo_path, guide_path)
    ```

    For example:

    ```python
    create_auto_guide("/path/to/your/model.usda", "/path/to/save/guide.usda")
    ```

4. The script will generate a USD stage containing the auto guide cube mesh based on the bounding box of your 3D model. The guide will be saved at the specified guide_path.

Please note that this script assumes that you have a valid USD model(has a default_prim and the correct UP hierarchy) at the model_geo_path. Ensure that you have set up the paths to your model and guide correctly before running the script.

## Function Details

The script provides the following functions:

- `_get_extent(stage, prim)`: Calculates and sets the extents of a given primitive based on its world bounds.

- `_get_vertex_bbox(stage, prim)`: Calculates and sets the extents of a given primitive based on its world bounds and provides vertex points of the bounding box.

- `_create_cube_mesh(stage, bbox_extent, vertex_points, default_prim)`: Creates a cube mesh in the USD stage with the provided parameters, including the bounding box extent and vertex points.

- `create_auto_guide(model_path, guide_path)`: The main function that generates the auto guide for the 3D model and saves it to the specified path.

Each function is documented with additional details, input parameters, and potential exceptions it may raise.