import os
import argparse
import textwrap
import nibabel as nib
import numpy as np

def runTractography(subject,subjectLocation,outDir,side):

    thalamus_mask = os.path.join('/ccnc/chrconThalamus',
            subject,
            'ROI',
            side + '_thalamus.nii.gz')

    thalamus_mask_c = os.popen('fslstats {0} -C'.format(
        thalamus_mask)).read().split(' ')

    x_centre = float(thalamus_mask_c[0])
    y_centre = float(thalamus_mask_c[1])
    z_centre = float(thalamus_mask_c[2])


    # Make mask
    # that covers all brain areas anterior to the center of the thalamus
    thalData = nib.load(thalamus_mask)
    thal_array = thalData.get_data()
    thal_array[:,:,z_centre:] = 1
    new_thalData = nib.Nifti1Image(thal_array, thalData.affine)
    new_thalData_loc = os.path.join(outDir,'new_'+os.path.basename(thalamus_mask))
    new_thalData.to_filename(new_thalData_loc)

    
    # take thalamus out from the mask
    newMask = os.path.join(outDir,'thal_subt_new_'+os.path.basename(thalamus_mask))
    thal_subtract = os.popen('fslmaths {mas} -sub {thal} {newMask}'.format(
        mas = new_thalData_loc,
        thal = thalamus_mask,
        newMask = newMask)).read()


    fdt_path = os.path.join(outDir,'fdt_paths.nii.gz')

    fdt_merge_command = os.popen('fslmaths {tract_orig} -mas {mask} {outputImg}'.format(
        tract_orig = fdt_path,
        mask = newMask,
        outputImg = os.path.join(outDir,'new_fdt_paths.nii.gz'))).read()


    # threshold 70%
    command = 'fslmaths {fdt} -thrP 70 {out}'.format(
            fdt = os.path.join(outDir,'new_fdt_paths.nii.gz'),
            out = os.path.join(outDir,'thr_new_fdt_paths.nii.gz'))
    os.popen(command).read()


    print 'fslview {brain} {fdt} -l "Red-Yellow"'.format(
    #print 'fslview {brain} {fdt} -b {trackMin},{trackMax} -l "Red-Yellow"'.format(
            brain=os.path.join('/ccnc/chrconThalamus',subject,'freesurfer/mri/brain.nii.gz'),
            fdt = os.path.join(outDir,'thr_new_fdt_paths.nii.gz'))
            #trackMin = trackThr,
            #trackMax = trackMax)

    # FA map
    command = 'flirt -in {fdt} -applyxfm -init {mat} -ref {dti} -out {fdt_dti}'.format(
            fdt = os.path.join(outDir,'thr_new_fdt_paths.nii.gz'),
            mat = os.path.join('/ccnc/chrconThalamus',subject,
                               'registration','freesurferT1toNodif.mat'),
            dti = os.path.join('/ccnc/chrconThalamus',subject,'DTI','nodif_brain.nii.gz'),
            fdt_dti = os.path.join(outDir,'fdt_dti.nii.gz'))

    os.popen(command).read()

    FA_threshold = 0.22

    FA_masked_command = 'fslmaths {FA} -mas {mask} {FA_masked}'.format(
            FA = os.path.join('/ccnc/chrconThalamus',subject,'DTI','dti_FA.nii.gz'),
            mask = os.path.join(outDir,'fdt_dti.nii.gz'),
            FA_masked = os.path.join(outDir,'FA_masked.nii.gz'))

    os.popen(FA_masked_command).read()

    FA_masked_threshold_command = 'fslmaths {FA_masked} -thr {thr} {FA_masked_thresholded}'.format(
            FA_masked = os.path.join(outDir,'FA_masked.nii.gz'),
            thr = FA_threshold,
            FA_masked_thresholded = os.path.join(outDir,'FA_masked_thr.nii.gz'))

    os.popen(FA_masked_threshold_command)



    
    


if __name__=='__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            {codeName} : runs tractography
            ========================================
            eg) runTractography -s CHR02_JHJ -o /Users/admin/Desktop/prac_4_python
            '''.format(codeName=os.path.basename(__file__))))
    parser.add_argument(
        '-s', '--subject',
        help='name of the subject directory',
        default=os.getcwd())

    parser.add_argument(
        '-o', '--out',
        help='output directory')

    parser.add_argument(
        '-l', '--left',
        help='left side',
        action='store_true')

    parser.add_argument(
        '-r', '--right',
        help='right side',
        action='store_true')
    args = parser.parse_args()


    if args.left and args.right:
        parser.error('Please choose only one side')
    elif args.left:
        side = 'lh'
    else:
        side = 'rh'

    runTractography(args.subject,
            os.path.join('/ccnc/chrconThalamus',args.subject),
            args.out,
            side)
