import numpy as np
import sphere_snap.utils as snap_utils
import sphere_snap.sphere_coor_projections as sphere_proj
from sphere_snap.snap_config import SnapConfig, ImageProjectionType
from sphere_snap.sphere_snap import SphereSnap
from scipy.spatial.transform import Rotation as R
from sphere_snap.top_view import TopViewProjector


def __rot(yaw, pitch):
    return R.from_euler("yxz",[yaw,-pitch,0], degrees=True).as_quat()

def get_cube_map_faces(face_size=1440, source_img_hw=(2000,4000), source_img_type=ImageProjectionType.EQUI):
    
    snap_configs = [SnapConfig( __rot(90*i,0), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type)
                        for i in range(4)]
    # top
    snap_configs.append(SnapConfig( __rot(0,90), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type))
    # bottom
    snap_configs.append(SnapConfig( __rot(0,-90), (face_size,face_size),(90,90), source_img_hw, source_img_type=source_img_type))
    return snap_configs


def equi2cubemap(equi_img, face_size=None):
    """
    Converts image from equirectangular projection into cubemap
    :param equi_img:  equirectangular source image numpy array
    :param face_size:  [optional] cubemap face pixels resolution
    Returns a list of 6 images representing cubemap faces [ f, l, r, b, t, b]
    """
    face_res = face_size if face_size is not None else equi_img.shape[1]//4
    cube_configs = get_cube_map_faces(face_size=face_res, source_img_hw=equi_img.shape[:2])
    cube_faces_snaps = [SphereSnap(c) for c in cube_configs]
    cube_faces_imgs = [snap.snap_to_perspective(equi_img) for snap in cube_faces_snaps]
    return cube_faces_imgs

def cubemap2equi(cubemap_faces, out_hw=None):
    """
    Converts image from cubemap into equirectangular
    :param cubemap_faces:  a list of 6 images representing cubemap faces [ f, l, r, b, t, b]
    :param out_hw:  [optional] equirectangular resolution
    Returns equirectangular image as numpy array
    """
    face_size = cubemap_faces[0].shape[0]
    equi_hw = out_hw if out_hw is not None else np.array([2*face_size, 4*face_size]).astype(int)
    cube_configs = get_cube_map_faces(face_size=face_size, source_img_hw=equi_hw)
    cube_faces_snaps = [SphereSnap(c) for c in cube_configs]
    out_equi = SphereSnap.merge_multiple_snaps( equi_hw, 
                                                cube_faces_snaps, # snap object specifies destination position
                                                cubemap_faces, # snap image contains planar image pixels
                                                target_type=ImageProjectionType.EQUI, # destination image type
                                                merge_method="max")
    return out_equi


def cubemap2fisheye(cubemap_faces, h_angle_offset = 0, out_hw=None):
    """
    Converts image from cubemap into a 180 fisheye image
    :param cubemap_faces:  a list of 6 images representing cubemap faces [ f, l, r, b, t, b]
    :param out_hw:  [optional] fisheye resolution
    :param h_angle_offset:  [optional] start angle offset, if 0 first image is looking forward
    Returns a fisheye image as numpy array
    """
    face_size = cubemap_faces[0].shape[0]
    fisheye_hw = out_hw if out_hw is not None else np.array([2*face_size, 2*face_size]).astype(int)
    cube_configs = get_cube_map_faces(face_size=face_size)

    for snap_config in cube_configs:
        r = R.from_euler("yxz",[h_angle_offset,0,0], degrees=True).as_matrix()
        m = snap_config.transform.as_matrix().dot(r)
        snap_config.set_transform(R.from_matrix(m)) 

    cube_faces_snaps = [SphereSnap(c) for c in cube_configs]
    out_img = SphereSnap.merge_multiple_snaps( fisheye_hw, 
                                                cube_faces_snaps, # snap object specifies destination position
                                                cubemap_faces, # snap image contains planar image pixels
                                                target_type=ImageProjectionType.FISHEYE_180, # destination image type
                                                merge_method="max")
    return out_img

def equi2fisheye(equi_img):
    """
    Converts image from equirectangular into two 180 fisheye images
    :param equi_img:  equirectangular source image numpy array
    Returns a list of two fisheye images as numpy array
    """
    cube_faces_imgs = equi2cubemap(equi_img)
    f = cubemap2fisheye(cube_faces_imgs, h_angle_offset = 0)
    b = cubemap2fisheye(cube_faces_imgs, h_angle_offset = 180)
    return [f,b]

def fisheye2equi(fisheye_img, back_fisheye_img=None, out_hw=None):
    """
    Converts image from two 180 fisheye images into one equirectangular
    :param fisheye_img:  front fisheye source image, numpy array
    :param back_fisheye_img:  back fisheye source image, numpy , is optional
    :param out_hw:  [optional] equirectangular output resolution
    Returns a equirectangular image as numpy array
    """

    eq_hw = out_hw if out_hw is not None else np.array([fisheye_img.shape[0], 2*fisheye_img.shape[0]])
    size = int(fisheye_img.shape[0] * 0.7)    
    snap_configs = [SnapConfig( __rot(yaw,pitch), (size,size), (110,110), fisheye_img.shape[:2], source_img_type=ImageProjectionType.FISHEYE_180) 
                    for yaw,pitch in [[45,0],[-45,0],[0,45],[0,-45]]]
    snaps = [SphereSnap(c) for c in snap_configs]
    snap_imgs = [snap.snap_to_perspective(fisheye_img) for snap in snaps]

    if back_fisheye_img is not None:
        back_snap_imgs = [snap.snap_to_perspective(back_fisheye_img) for snap in snaps]
        for snap_config in snap_configs:
            r = R.from_euler("yxz",[180,0,0], degrees=True).as_matrix()
            m = snap_config.transform.as_matrix().dot(r)
            snap_config.set_transform(R.from_matrix(m)) 
        b_snaps = [SphereSnap(c) for c in snap_configs]
        snaps.extend(b_snaps)
        snap_imgs.extend(back_snap_imgs)

    reconstructed_equi = SphereSnap.merge_multiple_snaps(eq_hw, 
                                                     snaps, # snap object specifies destination position
                                                     snap_imgs, # snap image contains planar image pixels
                                                     target_type=ImageProjectionType.EQUI, # destination image type
                                                     merge_method="max")
    return reconstructed_equi


def equi2tv(equi_img, upright_rotation, out_hw, fov, tv_height_m, equi_height_m):
    """
    Reprojects to top view image from an equirectangular image
    :param equi_img: source equirectangular image
    :param upright_rotation: rotation from the ground plane
    :param out_hw: output resolution of the top view image
    :param fov_deg: field of view in degress of the top view image
    :param tv_height_m: height in meters of the top view image
    :param equi_height_m: height in meters of the equi image
    """
    tvp = TopViewProjector(out_hw, fov,tv_height_m)
    tv_img = tvp.extract_tv(equi_img, upright_rotation, equi_height_m)
    return tv_img
