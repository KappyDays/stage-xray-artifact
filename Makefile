.PHONY: reproduce test verify

reproduce:
	python -m stage_xray_artifact reproduce --data data/publication_safe --out build/reproduction --verify

test:
	python -m unittest discover -s tests -v

verify: reproduce test
