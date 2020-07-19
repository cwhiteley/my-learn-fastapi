SHELL := /bin/bash

inputs = a_intro.md b_di.md c_authentication.md d_db.md e_advanced.md f_graphql.md g_websockets.md h_pydantic.md

all: README.md

.PRECIOUS: README.md
README.md: $(inputs) Makefile
	# Collect
	cat $(inputs) > README.md

.INTERMEDIATE: $(inputs)
$(inputs): %.md: %.py
	echo "# $<" > $@
	echo '```python' >> $@
	cat $< >> $@
	echo '```' >> $@
	echo >> $@
