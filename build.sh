python setup.py sdist wheel
twine check dist/*
twine upload dist/*