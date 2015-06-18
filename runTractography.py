#!/ccnc_bin/venv/bin/python

import os
import argparse
import textwrap

'''
It runs probabilistic tractography using probtrackx2 in FSL.
In the script, 
    - the seed and the target ROI have been set as
        - thalamus ROI
        - OFC ROI
    - using network option (obtaining the tract between seed and target)
    - in T1 space (Therefore, the transformation matrix is used as well.)

The script assumes that the 'subject' is in 
    - '/ccnc/chrconThalamus' for CHR
    - '/ccnc/chrconThalamus/SPD' for FEP

and also assumes that DTI bedpostx have been completed in each subject as
    - {subject}/DTI.bedpostX

Future updates for more general usage
    - Direct inputs from the shell
        - ROIs
        - Transformation matrix
        - data location
'''


def runTractography(subject,subjectLocation,outDir,side):
    try:
        os.mkdir(outDir)
    except:
        pass
    
    mask = '{thalamus_ROI_Location}\n{OFC_ROI_Location}\n'.format(
                thalamus_ROI_Location =os.path.join(subjectLocation,'ROI','{0}_thalamus.nii.gz'.format(side)),
                OFC_ROI_Location = os.path.join(subjectLocation,'ROI','{0}_OFC.nii.gz'.format(side)))
    
    with open(os.path.join(outDir,'masks.txt'),'w') as f:
        f.write(mask)
    
    
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
--forcedir \
--opd \
-s {subjectLocation}/DTI.bedpostX/merged \
-m {subjectLocation}/DTI.bedpostX/nodif_brain_mask \
--dir={outDir}'.format(mask = os.path.join(outDir,'masks.txt'),
                       subjectLocation = subjectLocation,
                       outDir = outDir)
    print command
    print os.popen(command).read()

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
        help='name of the subject directory')
        

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


    if args.subject == None: 
        parser.error('Please choose a subject')

    if args.left and args.right:
        parser.error('Please choose only one side')
    elif args.left:
        side = 'lh'
    else:
        side = 'rh'

    if args.subject.startswith('FEP'):
        runTractography(args.subject,
                os.path.join('/ccnc/chrconThalamus/SPD',args.subject),
                args.out,
                side)
    else:
        runTractography(args.subject,
                os.path.join('/ccnc/chrconThalamus',args.subject),
                args.out,
                side)
