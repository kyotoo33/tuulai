# Tuulai — a solo learning workspace. `make run` and open http://127.0.0.1:8642
PY := .venv/bin/python
PORT ?= 8642

setup:          ## create the venv and install dependencies (run this first)
	python3 -m venv .venv && $(PY) -m pip install -q --upgrade pip && $(PY) -m pip install -q -r requirements.txt
	@echo "Ready. Now: make check && make dev"

.PHONY: setup run dev test check notify coach install-agents uninstall-agents clean

run:            ## start the app (production-ish)
	$(PY) -m uvicorn backend.main:app --host 127.0.0.1 --port $(PORT)

dev:            ## start with auto-reload for editing content/code
	$(PY) -m uvicorn backend.main:app --host 127.0.0.1 --port $(PORT) --reload

test:           ## run the unit tests
	$(PY) -m pytest tests/ -q

check:          ## import-validate all content (fails on any bad card/problem/latex)
	$(PY) -c "from backend import content as C; import json; print(json.dumps(C.summary(), indent=2))"

notify:         ## fire one desktop notification now (test the nudge)
	$(PY) tools/notify/notify.py

coach:          ## print the weekly coach report as JSON
	@curl -s http://127.0.0.1:$(PORT)/api/coach | $(PY) -m json.tool

install-agents: ## install macOS LaunchAgents (keep-alive server + daily afternoon nudge)
	bash tools/notify/install.sh

uninstall-agents: ## remove the LaunchAgents
	bash tools/notify/uninstall.sh

clean:          ## drop the local state DB (keeps content)
	rm -f data/tuulai.db
