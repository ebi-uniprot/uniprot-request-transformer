#!/bin/bash
LOG_PARSING_DIRECTORY=/hps/nobackup/production/uniprot/logs/2022v3

TRANSFORMED_DIRECTORY=$LOG_PARSING_DIRECTORY/transformed
MAP_DIRECTORY=$TRANSFORMED_DIRECTORY/map
OUT_DIRECTORY=$TRANSFORMED_DIRECTORY/out
ERROR_DIRECTORY=$TRANSFORMED_DIRECTORY/error

mkdir -p $TRANSFORMED_DIRECTORY
mkdir -p $MAP_DIRECTORY
mkdir -p $OUT_DIRECTORY
mkdir -p $ERROR_DIRECTORY

PARSED_DIRECTORY=$LOG_PARSING_DIRECTORY/reduce/parsed
FILE_LIST=$TRANSFORMED_DIRECTORY/file_list.txt

find $PARSED_DIRECTORY -name "*.csv" > $FILE_LIST
n=$(wc -l < $FILE_LIST)

mem=5000

bsub \
-J"transform[1-$n]" \
-M $mem \
-R"select[mem>$mem] rusage[mem=$mem] span[hosts=1]" \
-o $OUT_DIRECTORY/%J-%I \
-e $ERROR_DIRECTORY/%J-%I \
./transformer_map_wrapper.sh $FILE_LIST $MAP_DIRECTORY
