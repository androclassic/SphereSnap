# SphereSnap
A quick and easy to use library for reprojecting various image types. (inspired by http://paulbourke.net/panorama/sphere2persp/ ) 

## Examples and usecases
### Reprojecting equirectangular image into pinhole-camera images with customizable FoV and resolution
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/236621219-457eae8c-ad88-452d-8e89-8b16e4750dd1.jpg">
<img width="320" alt="image" src="https://user-images.githubusercontent.com/1941529/236621440-5f2fa7f1-b072-4aff-8596-48b236c1d60f.jpg">

### Create equirectangular image using cubemap faces
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/236621503-b5cf5e22-6a89-41c1-8765-3c5d23c1df1d.png">

### Create fisheye images from equirectangular or cubemap images
<img width="320" alt="image" src="https://user-images.githubusercontent.com/1941529/236621560-cf9f5344-d041-4769-8b86-c52efa2958f6.png">
### Create top view images from equirectangular/fisheye/planar images
<img width="320" alt="image" src="https://user-images.githubusercontent.com/1941529/236621633-4c6b30b5-0141-4a43-95fd-e93409d56d3e.png">

### Correct radially distorted images
<img width="320" alt="image" src="https://user-images.githubusercontent.com/1941529/236621823-a32b57f9-ec4c-4d8c-b45d-f5cda1dbaecc.png">


## How to use it

Module sphere_snap.reprojections contains easy to use functions for simple situations: 
- equi2cubemap
- cubemap2equi
- cubemap2fisheye
- equi2fisheye
- fisheye2equi
- equi2tv

For more complex situtation SphereSnaper can be used which is more flexible

```python
import sphere_snap.utils as snap_utils
import sphere_snap.sphere_coor_projections as sphere_proj
from sphere_snap.snap_config import SnapConfig, ImageProjectionType
from sphere_snap.sphere_snap import SphereSnap
import sphere_snap.reprojections as rpr

```

## Snap to perspective from equirectangular
```python
snap_config = SnapConfig( [0,0,0,1], (1400,1400),(120,120), equi_photo.shape[:2], source_img_type=ImageProjectionType.EQUI)
snap_test = SphereSnap(snap_config)
persp_img = snap_test.snap_to_perspective(equi_photo)
```
## Reproject equirectangular into 6 planar images of 90 degrees FoV (Cubemap)
```python
def get_cube_map_faces(face_size=1440, source_img_hw=(2000,4000), source_img_type=ImageProjectionType.EQUI):
    
    snap_configs = [SnapConfig( rot(90*i,0), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type)
                        for i in range(4)]
    # top
    snap_configs.append(SnapConfig( rot(0,90), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type))
    # bottom
    snap_configs.append(SnapConfig( rot(0,-90), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type))
    return snap_configs

cube_configs = get_cube_map_faces(face_size=1440, source_img_hw=equi_img.shape[:2])
cube_faces_snaps = [SphereSnap(c) for c in cube_configs]
cumbe_faces_imgs = [snap.snap_to_perspective(equi_img) for snap in cube_faces_snaps]
    
```
or
```python
cube_faces_imgs = rpr.equi2cubemap(equi_img)
```

## Reproject a planar image into equirectangular
```python
reconstructed_equi = SphereSnap.merge_multiple_snaps((1000,2000), 
                                                     cube_faces_snaps, # snap object specifies destination position
                                                     cumbe_faces_imgs[::-1], # snap image contains planar image pixels
                                                     target_type=ImageProjectionType.EQUI, # destination image type
                                                     merge_method="max")
```
## Reproject a planar image into fisheye 180
```python
reconstructed_fisheye = SphereSnap.merge_multiple_snaps((1000,1000), 
                                                    cube_faces_snaps, # snap object specifies destination position
                                                    cumbe_faces_imgs, # snap image contains planar image pixels
                                                    target_type=ImageProjectionType.FISHEYE_180, # destination image type
                                                    merge_method="max")                                                    
```

## Snap to perspective from fisheye 180
```python
snap_config = SnapConfig( rot(45,1), (1400,1400),(100,100), reconstructed_fisheye.shape[:2], source_img_type=ImageProjectionType.FISHEYE_180)
snap_test = SphereSnap(snap_config)
persp_img = snap_test.snap_to_perspective(reconstructed_fisheye)
```

## Reproject fisheye 180 to equirectangular
```python
snap_configs = [SnapConfig( rot(yaw,pitch), (800,800),(90,90), fisheye180_img.shape[:2], source_img_type=ImageProjectionType.FISHEYE_180) 
                    for yaw,pitch in [[-45,-45],[45,-45],[-45,45],[45,45],[0,0]]]
snaps = [SphereSnap(c) for c in snap_configs]
snap_imgs = [snap.snap_to_perspective(fisheye180_img) for snap in snaps]

reconstructed_equi = SphereSnap.merge_multiple_snaps((1000,2000), 
                                                     snaps, # snap object specifies destination position
                                                     snap_imgs, # snap image contains planar image pixels
                                                     target_type=ImageProjectionType.EQUI, # destination image type
                                                     merge_method="max")

```
