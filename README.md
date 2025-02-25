# napari 3d counter postproc

This package contains functions and commands related to napari 3d counter

## Instalation
pip install git+https://github.com/pnewstein/n3d-counter-postproc/ -U

## Usage

### Commands
- ```read-into-napari``` 
    - reads a bitplane ims file into napari 3d counter. Adding all of the image layers to the image
    - reads spots as cells in napari-3d-counter
    - for more details see ```read-into-napari --help```

### Functions
- ```segment_by_shapes```
    -  takes a shapes layer and uses it to split up the labels of a napari 3d counter
    - arguments are viewer, and path to a csv file made by napari-3d-counter
    - optionaly takes two other paths for the layers whith changed names, and
      the summary including the number of points in each category
- ```read_into_napari```
    - view an imaris file with napari-3d-counter
    - optionaly takes in a viewer, and can optionaly load the low res version

