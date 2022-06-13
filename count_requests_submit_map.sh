#!/bin/bash
WORKING_DIRECTORY=/nfs/public/rw/homes/uni_adm/log-analysis/logs/2022v2

DAILY_DIRECTORY=$WORKING_DIRECTORY/daily
RPM_DIRECTORY=$WORKING_DIRECTORY/rpm
OUT_DIRECTORY=$RPM_DIRECTORY/out
ERROR_DIRECTORY=$RPM_DIRECTORY/error

mkdir -p $RPM_DIRECTORY
mkdir -p $OUT_DIRECTORY
mkdir -p $ERROR_DIRECTORY

FILE_LIST=$RPM_DIRECTORY/file_list.txt

find $DAILY_DIRECTORY -name "*.csv" > $FILE_LIST
n=$(wc -l < $FILE_LIST)

mem=5000

bsub \
-J"rpm[1-$n]" \
-M $mem \
-R"select[mem>$mem] rusage[mem=$mem] span[hosts=1]" \
-o $OUT_DIRECTORY/%J-%I \
-e $ERROR_DIRECTORY/%J-%I \
./count_requests_map_wrapper.sh $FILE_LIST 
