.PHONY: audit-locations

audit-locations:
	python3 scripts/audit_locations.py --fail-on-high
