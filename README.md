# Digital Forensics Toolkit

Forensic evidence collection and analysis toolkit for systems suspected of
compromise. Supports a defensible workflow aligned with **NIST SP 800-86** and
**DFIR** best practices.

**Tools covered:** Autopsy, The Sleuth Kit (TSK), Volatility, FTK Imager.
**Skills demonstrated:** Disk and memory forensics, chain of custody, evidence handling.

---

## Workflow

```
  Acquire ──> Preserve ──> Analyze ──> Report
   (image/    (hash +      (TSK /     (documented
    artifact)  chain of     Volatility) chain of
               custody)                custody)
```

1. **Acquire** – create a bit-stream disk image (`dd` / FTK Imager) and a memory
   capture (Volatility) from the compromised system.
2. **Preserve** – record SHA-256 hashes and log every hand-off in the
   chain-of-custody log. Never analyze the original evidence.
3. **Analyze** – use TSK/Autopsy for disk artifacts and Volatility for memory
   (processes, network, injected code).
4. **Report** – produce an evidence report with timestamps, hashes, and findings.

---

## Contents

| Path | Description |
|------|-------------|
| `scripts/forensics_toolkit.py` | Main CLI: artifact collection, hashing, chain-of-custody log, imaging/TSK/Volatility command builder |
| `docs/evidence_handling.md` | Evidence-handling standard (do's / don'ts, preservation) |
| `docs/chain_of_custody.md` | How chain of custody is tracked in this toolkit |
| `templates/evidence_report.md` | Evidence report template |
| `templates/chain_of_custody.md` | Printable chain-of-custody form |
| `evidence/` | Runtime output (auto-created): hashes, reports, chain log |

---

## Quick start

```bash
# Collect an artifact with a chain-of-custody entry
python scripts/forensics_toolkit.py collect --path /tmp/malware.bin --handler "A. Analyst"

# Show the dd imaging command for a disk
python scripts/forensics_toolkit.py image --source /dev/sda --dest /evidence/disk1.raw

# Show Sleuth Kit analysis commands for a disk image
python scripts/forensics_toolkit.py tsk --image /evidence/disk1.raw

# Show Volatility memory-analysis commands for a memory image
python scripts/forensics_toolkit.py memory --file /evidence/mem.raw

# Print the chain-of-custody log
python scripts/forensics_toolkit.py chain
```

## Tool reference

| Task | Tool | Example |
|------|------|---------|
| Disk imaging | FTK Imager / `dd` | `sudo dd if=/dev/sda of=disk1.raw bs=4M conv=noerror,sync` |
| File-system analysis | Sleuth Kit | `fls -r -p disk1.raw`, `fsstat disk1.raw`, `mmls disk1.raw` |
| GUI analysis | Autopsy | open the image / case in Autopsy |
| Memory capture | Volatility / memdump | create a `.raw` / `.mem` dump |
| Memory analysis | Volatility 3 | `vol3 -f mem.raw windows.malfind` |