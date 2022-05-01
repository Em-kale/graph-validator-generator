#!/bin/bash

FILE=$1
if [[ -f "$FILE" ]]; then
    echo "$FILE exists."
else 
    if [[ -d generated_graphs ]]; then
        cp -r template generated_graphs/$1
    else 
        mkdir generated_graphs 
        cp -r template generated_graphs/$1
    fi
fi