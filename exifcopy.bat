rem First argument is the file to copy from.
rem Second argument is the file to copy to.
exiftool -overwrite_original -all:all= %2
exiftool -overwrite_original -TagsFromFile %1 "-all:all>all:all" %2
