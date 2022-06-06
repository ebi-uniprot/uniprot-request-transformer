#!/bin/bash
FILE_LIST=$1
RESULTS_DIRECTORY=$2
FILE=$(head -n $LSB_JOBINDEX $FILE_LIST | tail -1)
/homes/dlrice/uniprot-request-transformer/transformer.py $FILE ${FILE}.gatling
exit $?