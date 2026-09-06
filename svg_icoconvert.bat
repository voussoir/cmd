set tempfolder=T:\temp\%random%%random%%random%
md %tempfolder%
svgrender %1 16 32 48 64 128 256 --destination %tempfolder%
icoconvert %tempfolder%\*.png --output %~n1.ico
