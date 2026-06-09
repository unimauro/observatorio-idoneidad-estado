.PHONY: install etl api dashboard graph test
install:    ; pip install -r requirements.txt
etl:        ; python -m observatorio.etl.pipeline
graph:      ; python -m observatorio.graph.load_neo4j
api:        ; uvicorn observatorio.api.main:app --reload --port 8000
dashboard:  ; streamlit run dashboard/app.py
test:       ; PYTHONPATH=src pytest -q
