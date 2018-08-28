import os
import subprocess
from os.path import join as jph

from DummyForMRI.generators import generate_multi_atlas, generate_labels_descriptor


if __name__ == '__main__':

    root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

    pfo_examples    = jph(root_dir, 'data_examples')
    pfo_multi_atlas = jph(pfo_examples, 'dummy_multi_atlas')

    if not os.path.exists(pfo_examples):
        os.system('mkdir {}'.format(pfo_examples))

    if os.path.exists(pfo_multi_atlas):
        os.system('rm -r {}'.format(pfo_multi_atlas))

    os.system('mkdir -p {}'.format(pfo_multi_atlas))

    number_of_subjects = 3
    name_ground_truth  = ('modGT', 'segmGT')
    name_modalities    = ('mod1', 'mod2')

    generate_multi_atlas(pfo_multi_atlas, number_of_subjects=number_of_subjects, multi_atlas_root_name='Danny',
                         randomness_shape=0.3, randomness_noise=0.4,
                         name_modalities=name_modalities, name_ground_truth=name_ground_truth)

    pfi_ld = jph(pfo_multi_atlas, 'labels_descriptor.txt')
    generate_labels_descriptor(pfi_ld)

    if subprocess.call(['which', 'itksnap']) == 0:
        print('Opening a subject with itksnap:\n')

        dummy_to_open = 'Danny3'
        pfo_dummy_to_open   = jph(pfo_multi_atlas, dummy_to_open)
        pfi_ground_truth    = jph(pfo_dummy_to_open, 'mod', '{}_{}.nii.gz'.format(dummy_to_open, name_ground_truth[0]))
        pfi_ground_segm     = jph(pfo_dummy_to_open, 'segm', '{}_{}.nii.gz'.format(dummy_to_open, name_ground_truth[1]))
        pfi_first_modality  = jph(pfo_dummy_to_open, 'mod', '{}_{}.nii.gz'.format(dummy_to_open, name_modalities[0]))
        pfi_second_modality = jph(pfo_dummy_to_open, 'mod', '{}_{}.nii.gz'.format(dummy_to_open, name_modalities[1]))

        os.system('itksnap -g {} -s {} -o {} {} -l {} '.format(pfi_ground_truth, pfi_ground_segm, pfi_first_modality,
                                                              pfi_second_modality, pfi_ld))
