#!/bin/bash

# Checking the size of the bader_charges.txt file 

echo -e $G"before: $(du -sh)"$dW
if [ -s bader_charges.txt ]; then
    rm AECCAR*
	echo -e $bR"rm AECCAR*"
	rm CHG*
	echo -e "rm CHG*"$dW
else
	echo -e $G"bader_charges.txt is empty"
fi
echo -e $Y"after: $(du -sh)"$dW
