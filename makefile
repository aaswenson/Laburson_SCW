clean:
	rm out* comou* srct* runt*

new_file:
	python make_scw.py
plot:
	mcnp6 ip i= scwr_2_region_homog.i
