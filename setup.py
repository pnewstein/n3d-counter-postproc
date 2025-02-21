from setuptools import setup

setup(
    name="n3d-counter-postproc",
    version="0.1.0",
    py_modules=["n3d_counter_postproc"],
    install_requires=[
        "pandas",
        "numpy",
        "napari",
        "imaris-ims-file_reader",
        "h5py",
        "click",
        "napari-3d-counter",
    ],
    author="Peter Newstein",
    author_email="peternewstein@gmail.com",
    description="some tools to do postprocessing on napari 3d counter points",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["read-into-napari = n3d_counter_postproc:main"]},
)
