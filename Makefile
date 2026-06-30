.PHONY: download publish publish-all clean

# Download a skill from a GitHub tree URL into pending-review/ for review.
#
# Usage:
#   make download https://github.com/owner/repo/tree/branch/path/to/skill
download:
	@bash scripts/download.sh $(filter-out $@,$(MAKECMDGOALS))

# Publish a single skill to future-server via the admin API.
# OVERWRITE defaults to false.
#
# Usage:
#   make publish future/future-account
#   make publish third-party/some-skill
#   OVERWRITE=true make publish future/future-account
publish:
	@bash scripts/publish.sh $(filter-out $@,$(MAKECMDGOALS)) $(OVERWRITE)

# Publish all skills in the future/ directory.
# OVERWRITE=true make publish-all
publish-all:
	@for d in future/*/; do \
		echo "=== Publishing $$d ==="; \
		bash scripts/publish.sh "$$d" $(OVERWRITE); \
	done

# Clean up generated artifacts in future-server/data/skills/
clean:
	rm -f ../future-server/data/skills/*.zip
	rm -f ../future-server/data/skills/skills-insert.sql

# Catch-all — prevents "No rule to make target" for the skill path argument.
%::
	@:
