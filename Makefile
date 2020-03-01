all:
	#
	# let's `make` life easier xD
	# 
	pip3 install invoke
	invoke list


docker:
	invoke docker
