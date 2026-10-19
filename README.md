# cost-tag-validator

Check the tagging taxonomy before finance asks you for cost per customer.

A cloud bill tells you what you spent. It does not tell you which customer spent it. That number comes from tags, and tags fail quietly: a key missing here, a value with different capitalisation there, and the monthly report splits into groups nobody can explain.

This tool reads Terraform, Helm and YAML files and checks every tagged resource against the taxonomy.

## The taxonomy

| Key | Example | Why |
|-----|---------|-----|
| `tenant_id` | `cust_88213` | direct customer attribution |
| `environment` | `prod` | split production from everything else |
| `service` | `checkout-api` | which workload |
| `cost_center` | `eng-42` | finance rollup |
| `owner` | `team-payments` | accountability |
| `tenancy` | `shared` or `dedicated` | the pivot: dedicated attributes directly, shared needs a split method |

Five keys are mandatory. `tenancy` decides whether the resource attributes directly or lands in the shared bucket, so the tool flags it when it is missing.

## Requirements

Python 3.9+, no dependencies.

## Usage

```
python3 cost_tag_validator.py ./infra
python3 cost_tag_validator.py . --report
```

```
Cost tag validator
==================================================================
  Path                    /home/you/infra
  Tagged resources found  118
  Fully compliant         96
  Attributable            81%

  Missing or invalid keys
    terraform/eks.tf          owner             no owner on this resource  (missing_key)
    helm/app/values.yaml     tenancy           tenancy must be shared or dedicated  (bad_tenancy)

  Case conflicts (these split your reports)
    owner         Team-Payments vs team-payments
```

Case conflicts are the quiet failure. `Team=Payments` and `Team=payments` are two different values to every cloud cost explorer, which is why a chart shows three groups when you expected one.

Exit code 0 when everything passes, 1 when there are problems.

## Report mode

`--report` prints one line for a runbook or a status report:

```
Cost tagging: 96 of 118 tagged resources carry the full taxonomy (81% attributable). Case conflicts on 1 key: Team-Payments vs team-payments. Checked 2026-10-20.
```

## Tests

```
python3 -m unittest test_cost_tag_validator -v
```

## Where this comes from

Written while preparing *Cost Per Customer: The Number Your Bill Never Shows*, built on the FinOps field guide data on multi-tenant cost attribution.

## License

MIT
