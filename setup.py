from setuptools import setup

setup(
    name='sphere_snap',
    version='0.1.0',    
    description='A quick and easy to use library for reprojecting various image types',
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
        'Development Status :: 1 - In progress',
        'Intended Audience :: Science/Research',
        'License :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)