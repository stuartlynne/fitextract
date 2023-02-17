
# vim: noexpandtab tabstop=8 shiftwidth=8



all:
	@echo "make sdist | install | bdist"

clean:
	rm -f */*pyc
	rm -rf build dist fitextract.egg-info

.PHONY: sdist install bdist

bdist sdist:
	python setup.py $@



