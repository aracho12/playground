#!/bin/bash

before = $1
after  = $2

files=$(ls "$before"*)

# change file name
for file in $files; do
  newname=$(echo $file | sed "s/$before/$after/")
  mv $file $newname
done
