#!/bin/bash

if test $# = '0'
then
    echo "error ファイルが指定されていません ファイル名を引数で与えてください 複数同時処理も可能です"
else
    for x in "$@"
    do
        filename=`basename "$x" | sed -e "s/\..*//g"`
	directoryname=`dirname "$x"`
	convert ${x} -resize 600x600 ${directoryname}/small-${filename}.jpg
    done
fi
