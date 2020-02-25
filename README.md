# misc_scripts
Image Parser:

Image Parser with read pairs of given Images from CSV File and generates Similarity index based on percentage of similarity
0.000 indicates two images are identical anything higher means the images are not similar.

It will generate the log file with same name as the input file with _result in the workspace.

Usage Instructions:
Step 1) Python 3 is required to run this program. Follow the instructions given in python.org to install python3.x
Step 2) Clone requirements.txt and the image_parser.py to your workspace.
Step 3) Install required libs using below command:
        pip install -r requirements.txt
Step 4) Copy the required Images you want to compare into the workspace, 
Step 5) Create a CSV File with image1,image2 format
Step 6) Run the below command.

Eg:

python image_parser.py image_diff -f image_list.csv

This will generate image_list_result.csv in the workspace.


For more details you can run 
python image_parser.py --help for furthur documentation.
