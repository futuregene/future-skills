.PHONY: download publish publish-all clean

# Download a skill from a GitHub tree URL into pending-review/ for review.
#
# Usage:
#   make download https://github.com/owner/repo/tree/branch/path/to/skill
download:
	@bash scripts/download.sh $(filter-out $@,$(MAKECMDGOALS))

# Publish a skill or all skills to future-server via the admin API.
# OVERWRITE defaults to false.
#
# Usage:
#   make publish builtin/future-account          # single skill
#   make publish third-party/some-skill         # single third-party skill
#   make publish all                            # all skills in builtin/ and third-party/
#   OVERWRITE=true make publish all             # overwrite all
publish:
	@skill="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ "$$skill" = "all" ]; then \
		for d in builtin/*/ third-party/*/; do \
			[ -d "$$d" ] || continue; \
			echo "=== Publishing $$d ==="; \
			bash scripts/publish.sh "$$d" $(OVERWRITE) || echo "=== SKIPPED (failed): $$d ==="; \
		done; \
	else \
		bash scripts/publish.sh "$$skill" $(OVERWRITE); \
	fi

# Publish all skills in builtin/ and third-party/ directories.
# Convenience alias for "make publish all".
# OVERWRITE=true make publish-all
publish-all:
	@$(MAKE) publish all OVERWRITE=$(OVERWRITE)

# Clean up generated artifacts in future-server/data/skills/
clean:
	rm -f ../future-server/data/skills/*.zip
	rm -f ../future-server/data/skills/skills-insert.sql

# Catch-all — prevents "No rule to make target" for the skill path argument.
%::
	@:
