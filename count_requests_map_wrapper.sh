#!/bin/bash
FILE_LIST=$1
FILE=$(head -n $LSB_JOBINDEX $FILE_LIST | tail -1)
/homes/dlrice/uniprot-request-transformer/count_requests.py $FILE 
exit $?