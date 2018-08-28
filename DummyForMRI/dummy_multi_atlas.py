import os
from os.path import join as jph

import nibabel as nib
import numpy as np
import scipy.ndimage.filters as fil

from DummyForMRI.building_blocks import sphere_shape
from DummyForMRI.dummy_atlas import headlike_phantom



def generate_labels_descriptor(pfi_where_to_save):
    descriptor_standard_header = \
"""################################################
# ITK-SnAP Label Description File
# File format:
# IDX   -R-  -G-  -B-  -A--  VIS MSH  LABEL
# Fields:
#    IDX:   Zero-based index
#    -R-:   Red color component (0..255)
#    -G-:   Green color component (0..255)
#    -B-:   Blue color component (0..255)
#    -A-:   Label transparency (0.00 .. 1.00)
#    VIS:   Label visibility (0 or 1)
#    IDX:   Label mesh visibility (0 or 1)
#  LABEL:   Label description
################################################
"""
    descriptor_data_for_atlas = \
"""    0     0     0     0      1.0     1     1    "Bkg"
    1   255     0     0      1.0     1     1    "Skull"
    2     0   255     0      1.0     1     1    "WM"
    3     0     0   255      1.0     1     1    "GM"
    4   255     0   255      1.0     1     1    "CSF"
"""
    with open(pfi_where_to_save, 'w+') as f:
        f.write(descriptor_standard_header)
        f.write(descriptor_data_for_atlas)
    print('Dummy labels descriptor saved under {}'.format(pfi_where_to_save))


def generate_atlas(pfo_where_to_save_atlas, atlas_name='t01', randomness_shape=0.3, randomness_noise=0.4,
                   name_modalities=('mod1', 'mod2'), name_ground_truth=('mod_GT', 'segmGT')):

    os.system('mkdir -p {}'.format(pfo_where_to_save_atlas))

    pfo_mod = jph(pfo_where_to_save_atlas, 'mod')
    pfo_segm = jph(pfo_where_to_save_atlas, 'segm')
    pfo_masks = jph(pfo_where_to_save_atlas, 'masks')

    os.system('mkdir {}'.format(pfo_mod))
    os.system('mkdir {}'.format(pfo_segm))
    os.system('mkdir {}'.format(pfo_masks))

    # B) Create modality and segmentation ground truth:
    intensities = (0.9, 0.3, 0.6, 0.8)
    omega = (80, 90, 80)
    print('in folder {}'.format(pfo_where_to_save_atlas))
    mod_gt, segm_gt = headlike_phantom(omega=omega, random_perturbation=randomness_shape, intensities=intensities)

    # B1) get roi mask (from the ground truth):
    print('- generate segmentation')
    roi_mask = segm_gt.astype(np.bool)

    # C) Create other modalities
    print('- generate other dummy-modalities')
    # -- invert intensities:
    mod_inv = 1 - mod_gt
    np.place(mod_inv, mod_inv == 1, 0)

    # -- add random noise: (25% of the randomness_noise for the background plus a gaussian filter of 50% size voxel)
    #     The noise granularity is fixed with parameters 10 and 3.
    noise_array = np.random.uniform(-10, 10, size=omega).astype(np.float64)
    noise_array = 0.25 * randomness_noise * fil.gaussian_filter(noise_array, 3)

    mod_gt_noise = mod_gt + noise_array

    noise_array = np.random.uniform(-10, 10, size=omega).astype(np.float64)
    noise_array = 0.25 * randomness_noise * fil.gaussian_filter(noise_array, 3)

    mod_inv_noise = mod_inv + noise_array

    # -- add hypo-intensities artefacts:
    num_spots = int(10 * randomness_noise / 2)
    noise_hypo = np.zeros_like(noise_array).astype(np.int32)
    for j in range(num_spots):
        radius_centre = 0.05 * randomness_noise * np.min(omega)
        random_radius = np.random.uniform(radius_centre - radius_centre/2, radius_centre + radius_centre/2)
        random_centre = [np.random.uniform(0 + random_radius, j - random_radius) for j in omega]

        noise_hypo = noise_hypo + sphere_shape(omega, random_centre, random_radius, foreground_intensity=1,
                                               dtype=np.int32)

    noise_hypo = 1 - 1 * (noise_hypo.astype(np.bool))
    # filter the results:
    mod_gt_noise = fil.gaussian_filter(mod_gt_noise * noise_hypo, 0.5 * randomness_noise)
    mod_inv_noise = fil.gaussian_filter(mod_inv_noise * noise_hypo, 0.5 * randomness_noise)

    # D) Get the Registration Mask (based on):
    reg_mask = noise_hypo * roi_mask

    # E) Generate nifti data structure
    im_segm_gt  = nib.Nifti1Image(segm_gt, affine=np.eye(4))
    im_mod_gt   = nib.Nifti1Image(mod_gt, affine=np.eye(4))
    im_mod1     = nib.Nifti1Image(mod_gt_noise, affine=np.eye(4))
    im_mod2     = nib.Nifti1Image(mod_inv_noise, affine=np.eye(4))
    im_roi_mask = nib.Nifti1Image(roi_mask.astype(np.int32), affine=np.eye(4))
    im_reg_mask = nib.Nifti1Image(reg_mask.astype(np.int32), affine=np.eye(4))

    # E) Save nifti data structure
    print('- saving... ')
    nib.save(im_mod_gt,   jph(pfo_mod,   '{}_{}.nii.gz'.format(atlas_name, name_ground_truth[0])))
    nib.save(im_segm_gt,  jph(pfo_segm,  '{}_{}.nii.gz'.format(atlas_name, name_ground_truth[1])))
    nib.save(im_mod1,     jph(pfo_mod,   '{}_{}.nii.gz'.format(atlas_name, name_modalities[0])))
    nib.save(im_mod2,     jph(pfo_mod,   '{}_{}.nii.gz'.format(atlas_name, name_modalities[1])))
    nib.save(im_roi_mask, jph(pfo_masks, '{}_roi_mask.nii.gz'.format(atlas_name)))
    nib.save(im_reg_mask, jph(pfo_masks, '{}_reg_mask.nii.gz'.format(atlas_name)))


def generate_multi_atlas(pfo_where_to_create_the_multi_atlas, number_of_subjects=10, multi_atlas_root_name='sj',
                         randomness_shape=0.3, randomness_noise=0.4,
                         name_modalities=('mod1', 'mod2'), name_ground_truth=('mod_GT', 'segmGT')):
    """
    Generate a phatom multi atlas of head-like shapes.
    This is based on nilabel.tools.phantoms_generator.shapes_for_headlike_phantoms.headlike_phantom
    and uses .generate_atlas_at_folder to generate a single element.
    :param pfo_where_to_create_the_multi_atlas: path to file where the multi atlas structure will be saved.
    :param number_of_subjects: [10] how many subjects in the multi atlas
    :param multi_atlas_root_name: root name for the multi atlas
    :param randomness_shape: randomness in the geometry of the backgorund shape. Must be between 0 and 1.
    :param randomness_noise: randomness in the simulated noise signal and artefacts. Must be between 0 and 1.
    :return:
    """
    os.system('mkdir -p {}'.format(pfo_where_to_create_the_multi_atlas))

    for sj in range(number_of_subjects):
        sj_name = multi_atlas_root_name + str(sj + 1).zfill(len(str(number_of_subjects)))
        print('\n\nCreating atlas {0} ({1}/{2})'.format(sj_name, sj+1, number_of_subjects))
        os.system('mkdir {}'.format(jph(pfo_where_to_create_the_multi_atlas, sj_name)))
        generate_atlas(jph(pfo_where_to_create_the_multi_atlas, sj_name), atlas_name=sj_name,
                       randomness_shape=randomness_shape, randomness_noise=randomness_noise,
                       name_modalities=name_modalities, name_ground_truth=name_ground_truth)
