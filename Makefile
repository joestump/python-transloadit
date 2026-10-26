.PHONY: test lint

test:
	python3 -m unittest discover -s tests -v

lint:
	python3 -m py_compile transloadit/client.py tests/test_client.py
