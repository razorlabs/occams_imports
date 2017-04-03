## Notes

During the process of adding codebooks and site data to the OCCAMS Imports Portal for UCSD, the codebooks need to be converted to appropriate formats.

## OCCAMS Codebooks

OCCAMS Codebooks are exported in a format where all form versions are included in the csv.  However, the preferred format would include
one merged ecrf rather than ecrfs with multiple versions.

To merge the codebooks, run the script:

* merge_ecrf_versions.py

## iForm Data

iForm data has the multiple versions issue, however the input file is in a data format (.json), which is different than OCCAMS codebooks.
Therefore the files need to be processed through two different scripts.

Run the following scripts on iForm codebook data in the following order:

* iform2occams.py
* merge_ecrf_versions.py

## OCCAMS Site Data

UCSD site data exported from OCCAMS is not in the correct format for file input into OCCAMS Imports.

Run the following script on OCCAMS site data prior to file upload:

* occams2drsc.py
