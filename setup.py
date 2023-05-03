from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
print(this_directory)
long_description = (this_directory / "README.md").read_text()


setup(
    name='sphere_snap',
    version='0.1.3',    
    description='A quick and easy to use library for reprojecting various image types',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/androclassic/SphereSnap',
    author='Andrei Georgescu',
    author_email='andrei.georgescu@yahoo.com',
    license='MIT License',
    packages=['sphere_snap'],
    install_requires=['scipy>=1.5.1',
                      'opencv-python',
                      'matplotlib',
                      'numpy',  
                      'logging'                   
                      ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
)