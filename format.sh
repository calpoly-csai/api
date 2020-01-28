

# --recursive: makes it work on folders
# --versbose: prints out the filename(s) while running 
# --in-place: actually modifies the file(s)
yapf --recursive --verbose --in-place *.py Entity/*.py modules/*.py
