import os
import re
import argparse
import textwrap

def runTractography(subject,subjectLocation,outDir,side):

    # Location set
    exclusionROI = os.path.join(outDir,'brain_stem.nii.gz')
    terminationROI = os.path.join(outDir,'stop_mask.nii.gz')
    roi_loc = os.path.join(subjectLocation,'ROI')
    thalamus_ROI = os.path.join(roi_loc,
                                '{0}_thalamus.nii.gz'.format(side))
    OFC_ROI = os.path.join(roi_loc,
                           '{0}_OFC.nii.gz'.format(side))
    mask = '{thalamus_ROI_Location}\n{OFC_ROI_Location}\n'.format(
                thalamus_ROI_Location = thalamus_ROI,
                OFC_ROI_Location = OFC_ROI)



    # Make output directory
    try:
        os.mkdir(outDir)
    except:
        pass
    

    # Make exclusion ROI : brain stem ROI
    brain_stem_extraction_command = 'mri_binarize \
            --i {aseg} \
            --match 16 \
            --o {outLoc}'.format(
                aseg = os.path.join(subjectLocation,
                                    'freesurfer',
                                    'mri',
                                    'aseg.mgz'),
                outLoc = exclusionROI)

    brain_stem_extraction_command = re.sub('\s+',' ',brain_stem_extraction_command)
    print brain_stem_extraction_command
    print os.popen(brain_stem_extraction_command).read()
    

    #Make ROI list as a text file : probtrackx2 input
    with open(os.path.join(outDir,'masks.txt'),'w') as f:
        f.write(mask)
    

    
    # Make termination ROI : LPFC + MPFC + LTC + MTC + PC + OCC + SMC
    merge_list = ['LPFC','MPFC','LTC','MTC','PC','OCC','SMC']
    merge_list_loc = [os.path.join(roi_loc,
                                   side+'_'+x+'.nii.gz') for x in merge_list]
    roi_merge_command = 'fslmaths {firstImg} {addList} {output}'.format(
            firstImg = merge_list_loc[0],
            addList = ' '.join(['-add '+x for x in merge_list_loc[1:]]),
            output = terminationROI)

    print os.popen(roi_merge_command).read()


    
    
    command = '/usr/local/fsl/bin/probtrackx2 \
                --network \
                -x {mask} \
                -l \
                --onewaycondition \
                -c 0.2 \
                -S 2000 \
                --steplength=0.5 \
                -P 5000 \
                --fibthresh=0.01 \
                --distthresh=0.0 \
                --sampvox=0.0 \
                --xfm={subjectLocation}/registration/freesurferT1toNodif.mat \
                --avoid={exclusionROI} \
                --stop={terminationROI} \
                --forcedir \
                --opd \
                -s {subjectLocation}/DTI.bedpostX/merged \
                -m {subjectLocation}/DTI.bedpostX/nodif_brain_mask \
                --dir={outDir}'.format(mask = os.path.join(outDir,'masks.txt'),
                                       exclusionROI = exclusionROI,
                                       terminationROI = terminationROI,
                                       subjectLocation = subjectLocation,
                                       outDir = outDir)
    probtrackx2_command = re.sub('\s+',' ',command)  
    print os.popen(probtrackx2_command).read()

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
