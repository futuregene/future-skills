.PHONY: download

# Download a skill from a GitHub tree URL into pending-review/ for review.
#
# Usage:
#   make download https://github.com/owner/repo/tree/branch/path/to/skill
download:
	@bash scripts/download.sh $(filter-out $@,$(MAKECMDGOALS))

# Catch-all — prevents "No rule to make target" for the skill path argument.
%::
	@:
