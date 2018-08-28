import os
import subprocess
from os.path import join as jph

from DummyForMRI.definitions import root_dir
from DummyForMRI.dummy_multi_atlas import generate_atlas, generate_labels_descriptor


if __name__ == '__main__':

    pfo_examples = jph(root_dir, 'data_examples')
    pfo_atlas    = jph(pfo_examples, 'Sam')

    if not os.path.exists(pfo_examples):
        os.mkdir(pfo_examples)

    if os.path.exists(pfo_atlas):
        os.system('rm -r {}'.format(pfo_atlas))

    os.system('mkdir -p {}'.format(pfo_atlas))

    number_of_subjects  = 3
    name_ground_truth   = ('modGT', 'segmGT')
    name_modalities     = ('mod1', 'mod2')

    generate_atlas(pfo_atlas, atlas_name='Sam', randomness_shape=0.3, randomness_noise=0.4,
                   name_modalities=name_modalities, name_ground_truth=name_ground_truth)

    pfi_ld = jph(pfo_examples, 'labels_descriptor.txt')
    generate_labels_descriptor(pfi_ld)

    if subprocess.call(['which', 'itksnap']) == 0:
        print('Opening a subject with itksnap:\n')

        id_to_open = 'Sam'
        pfi_ground_truth    = jph(pfo_atlas, 'mod', '{}_{}.nii.gz'.format(id_to_open, name_ground_truth[0]))
        pfi_ground_segm     = jph(pfo_atlas, 'segm', '{}_{}.nii.gz'.format(id_to_open, name_ground_truth[1]))
        pfi_first_modality  = jph(pfo_atlas, 'mod', '{}_{}.nii.gz'.format(id_to_open, name_modalities[0]))
        pfi_second_modality = jph(pfo_atlas, 'mod', '{}_{}.nii.gz'.format(id_to_open, name_modalities[1]))

        os.system('itksnap -g {} -s {} -o {} {} -l {}'.format(pfi_ground_truth, pfi_ground_segm, pfi_first_modality,
                                                              pfi_second_modality, pfi_ld))