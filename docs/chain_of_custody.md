# Chain of Custody

The toolkit maintains a machine-readable chain of custody at
`evidence/chain_of_custody.json`. Each entry records:

| Field | Meaning |
|-------|---------|
| `evidence_id` | Unique evidence identifier (e.g., `EVID-1A2B3C4D`) |
| `timestamp_utc` | When the action happened (UTC) |
| `action` | e.g. `acquired`, `transferred`, `analyzed`, `returned` |
| `handler` | Name/ID of the person handling the evidence |
| `details` | Artifact path, image, notes |

## Example
```json
[
  {
    "evidence_id": "EVID-809341D5",
    "timestamp_utc": "2026-08-18T13:53:35+00:00",
    "action": "acquired",
    "handler": "Analyst",
    "details": "artifact: /tmp/malware.bin"
  }
]
```

## Rules
- Every **hand-off** (who → who) must be logged before custody changes.
- The log itself should be hashed to detect tampering.
- Print and sign a physical form (see `templates/chain_of_custody.md`) for
  legal matters.
