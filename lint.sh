#flake8 . --count \ 
#         --select=E9,F63,F7,F82 \ 
#         --show-source \ 
#         --statistics \
#         --exclude .git,__pycache__,docs/source/conf.py,old,build,dist,venv \
#         --max-complexity 10
#
#
## stop the build if there are Python syntax errors or undefined names
#flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
## exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
#flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics



if [ $1 = "--simple" ]; then 
        # default is 79, but members of the team agreed upon a slight increase
        # The GitHub editor is 127 chars wide
        # ignore E772: do not use bare 'except'
        flake8 --count \
               --ignore E722 \
               --show-source --statistics \
               --exclude .git,__pycache__,venv,build,dist,docs \
               --max-complexity 10 \
               --max-line-length=127
else
        # default is 79, but members of the team agreed upon a slight increase
        # The GitHub editor is 127 chars wide
        flake8 --count \
               --show-source --statistics \
               --exclude .git,__pycache__,venv,build,dist,docs \
               --max-complexity 10 \
               --max-line-length=127
fi
