# Kasparro Agentic Facebook Analyst
# Commands for setup, running, and cleaning the project.

.PHONY: setup run run-custom clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup       - Install Python dependencies"
	@echo "  make run         - Run the analysis with the default query"
	@echo "  make query q=... - Run with a custom query (e.g., make query q='Check spend')"
	@echo "  make clean       - Remove reports, logs, and cache files"

# 1. Install Dependencies
setup:
	pip install -r requirements.txt

# 2. Run with Default Query
run:
	python run.py

# 3. Run with Custom Query
query:
	python run.py "$(q)"

# 4. Clean up artifacts
clean:
	rm -rf reports/ logs/
	rm -rf src/__pycache__/ src/agents/__pycache__/
	rm -rf memory/