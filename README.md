# SphereSnap
A quick and easy to use library for reprojecting various image types. (inspired by http://paulbourke.net/panorama/sphere2persp/ ) 

## Examples and usecases
### Reprojecting equirectangular image into pinhole-camera images with customizable FoV and resolution
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/227978179-f0c820d0-7a1e-470b-af85-ff5800addc8b.png">
<img width="320" alt="image" src="https://user-images.githubusercontent.com/1941529/227983634-d915aa5c-ca84-4124-8d1d-086568e4c9bd.png">

### Create equirectangular image using cubemap faces
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/227979707-1c30f125-6677-4c84-93e5-bb71e290a602.png">
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/227978179-f0c820d0-7a1e-470b-af85-ff5800addc8b.png">

### Create fisheye images from equirectangular or cubemap images
<img width="727" alt="image" src="https://user-images.githubusercontent.com/1941529/227982333-aa13a305-556a-40dd-83cf-aedbd6019b7b.png">


## How to use it
```python
import sphere_snap.utils as snap_utils
import sphere_snap.sphere_coor_projections as sphere_proj
from sphere_snap.snap_config import SnapConfig
from sphere_snap.sphere_snap import SphereSnap
```

## Snap to perspective from equirectangular
```python
snap_config = SnapConfig( [0,0,0,1], (1400,1400),(120,120), equi_img.shape[:2], source_img_type="equi")
snap_test = SphereSnap(snap_config)
persp_img = snap_test.snap_to_perspective(equi_img)
```
## Reproject equirectangular into 6 planar images of 90 degrees FoV (Cubemap)
```python
def get_cube_map_faces(face_size=1440, source_img_hw=(2000,4000), source_img_type="equi"):
    
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

## Reproject a planar image into equirectangular
```python
reconstructed_equi = SphereSnap.merge_multiple_snaps((1000,2000), 
                                                     cube_faces_snaps, # snap object specifies destination position
                                                     cumbe_faces_imgs[::-1], # snap image contains planar image pixels
                                                     target_type="equi", # destination image type
                                                     merge_method="max")
```
## Reproject a planar image into fisheye 180
```python
reconstructed_fisheye = SphereSnap.merge_multiple_snaps((1000,1000), 
                                                    cube_faces_snaps, # snap object specifies destination position
                                                    cumbe_faces_imgs, # snap image contains planar image pixels
                                                    target_type="fisheye180", # destination image type
                                                    merge_method="max")                                                    
```

## Snap to perspective from fisheye 180
```python
snap_config = SnapConfig( rot(45,1), (1400,1400),(100,100), reconstructed_fisheye.shape[:2], source_img_type="fisheye180")
snap_test = SphereSnap(snap_config)
persp_img = snap_test.snap_to_perspective(reconstructed_fisheye)
```

## Reproject fisheye 180 to equirectangular
```python
snap_configs = [SnapConfig( rot(yaw,pitch), (800,800),(90,90), fisheye180_img.shape[:2], source_img_type="fisheye180") 
                    for yaw,pitch in [[-45,-45],[45,-45],[-45,45],[45,45],[0,0]]]
snaps = [SphereSnap(c) for c in snap_configs]
snap_imgs = [snap.snap_to_perspective(fisheye180_img) for snap in snaps]

reconstructed_equi = SphereSnap.merge_multiple_snaps((1000,2000), 
                                                     snaps, # snap object specifies destination position
                                                     snap_imgs, # snap image contains planar image pixels
                                                     target_type="equi", # destination image type
                                                     merge_method="max")

```
