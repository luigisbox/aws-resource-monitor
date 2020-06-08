VENV_NAME?=venv

venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: setup.py
	@test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${VENV_NAME}/bin/python -m pip install -U pip
	${VENV_NAME}/bin/python -m pip install -e .
	@touch $(VENV_NAME)/bin/activate

black: venv
	@${VENV_NAME}/bin/python -m pip install black

flake8: venv
	@${VENV_NAME}/bin/python -m pip install flake8

fmt: venv black
	@${VENV_NAME}/bin/black .

fmtcheck: venv black
	@${VENV_NAME}/bin/black . -- --check --verbose

lint: venv flake8
	@${VENV_NAME}/bin/python -m flake8 --show-source aws_resource_monitor setup.py

clean:
	@rm -rf $(VENV_NAME) build/ dist/

.PHONY: venv fmt fmtcheck lint clean
