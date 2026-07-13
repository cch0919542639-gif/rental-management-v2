# ADR-0001: Monthly Bill Previous Balance

Status: Accepted
Date: 2026-07-12

## Decision

`MonthlyBill` stores `previous_balance` separately from `other_charges`.
The total due is calculated as:

```text
rent + electricity_amount + public_electricity + water_amount + other_charges + previous_balance
```

All calculated money values are rounded half-up to whole currency units.

## Rationale

Legacy bill `819` proves that a current-period charge can be correct while the
stored total also carries an earlier unpaid balance. Hiding that balance inside
`other_charges` makes both the current invoice and arrears untraceable.

## Consequences

- New generated bills snapshot earlier unpaid bills for the same contract.
- Existing historical bills are not bulk-recalculated; each imported anomaly
  needs evidence before assigning `previous_balance`.
- Payment reconciliation uses the full total due, including prior balance.
