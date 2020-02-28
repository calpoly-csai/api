all:
	#
	# let's `make` life easier xD
	# 
	pip install invoke
	invoke list


docker:
	invoke docker
