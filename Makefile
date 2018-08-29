all:
	python setup.py sdist

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

test:
	python setup.py test
