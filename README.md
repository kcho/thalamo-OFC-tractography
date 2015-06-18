# thalamo-OFC-tractography

### 2015.06.19

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
