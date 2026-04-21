.PHONY: audit-locations run-location-intake plan-enrichment-batch reconcile-enrichment-queue

MODE ?= stage
WRITE_REPORTS ?= 0

audit-locations:
	python3 scripts/audit_locations.py --fail-on-high

run-location-intake:
	@test -n "$(CSV)" || (echo "Usage: make run-location-intake CSV='data/climate/uploads/batch.csv' [MODE=stage|create] [WRITE_REPORTS=1] [ARGS='...']" >&2; exit 2)
	python3 scripts/run_location_intake.py --input-file "$(CSV)" --mode "$(MODE)" $(if $(filter 1 yes true,$(WRITE_REPORTS)),--write-reports,) $(ARGS)

plan-enrichment-batch:
	python3 scripts/plan_enrichment_batch.py $(ARGS)

reconcile-enrichment-queue:
	python3 scripts/reconcile_enrichment_queue.py $(ARGS)
