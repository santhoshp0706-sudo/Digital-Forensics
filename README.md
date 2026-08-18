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

## How to Run

### 1. Prerequisites
- **Python 3.8+** installed and on your `PATH`
  - Check: `python --version`
- The toolkit uses only the Python **standard library** — no `pip install` needed.

### 2. Clone the repository
```bash
git clone https://github.com/santhoshp0706-sudo/Digital-Forensics.git
cd Digital-Forensics
```

### 3. Verify the toolkit works
```bash
python scripts/forensics_toolkit.py --help
```
You should see the available commands:
```
usage: forensics_toolkit.py [-h] {collect,image,tsk,memory,chain} ...

Digital Forensics Toolkit

positional arguments:
  {collect,image,tsk,memory,chain}
    collect             Collect an artifact with chain of custody
    image               Show disk imaging command (dd)
    tsk                 Show Sleuth Kit commands for an image
    memory              Show Volatility commands for a memory image
    chain               Print chain-of-custody log
```

---

## Commands

### `collect` — collect an artifact with chain of custody
Hashes the file (SHA-256), records who/when it was acquired, and writes an
evidence report to `evidence/<EVID-ID>_report.json`.

```bash
# Linux / macOS
python scripts/forensics_toolkit.py collect --path /tmp/malware.bin --handler "A. Analyst"

# Windows
python scripts\forensics_toolkit.py collect --path C:\temp\malware.bin --handler "A. Analyst"
```
Output:
```
[chain-of-custody] 2026-08-18T13:53:35+00:00 | EVID-809341D5 | acquired | A. Analyst
[collect] evidence EVID-809341D5 -> evidence\EVID-809341D5_report.json
```

### `image` — show the disk imaging (`dd`) command
Prints the exact `dd` command to create a raw bit-stream image. Run it yourself
as root/sudo.

```bash
python scripts/forensics_toolkit.py image --source /dev/sda --dest /evidence/disk1.raw
```
Output:
```
sudo dd if=/dev/sda of=/evidence/disk1.raw bs=4M conv=noerror,sync status=progress
```

### `tsk` — show Sleuth Kit analysis commands
Prints the The Sleuth Kit (TSK) commands to run against your disk image.

```bash
python scripts/forensics_toolkit.py tsk --image /evidence/disk1.raw
```
Output:
```
fls -r -p /evidence/disk1.raw
fsstat /evidence/disk1.raw
mmls /evidence/disk1.raw
istat /evidence/disk1.raw <inode>
icat /evidence/disk1.raw <inode>
```

### `memory` — show Volatility analysis commands
Prints Volatility 3 plugin commands for a memory dump (`mem.raw` / `.vmem`).

```bash
python scripts/forensics_toolkit.py memory --file /evidence/mem.raw
```
Output:
```
vol3 -f /evidence/mem.raw windows.pslist
vol3 -f /evidence/mem.raw windows.cmdline
vol3 -f /evidence/mem.raw windows.netscan
vol3 -f /evidence/mem.raw windows.malfind
```

### `chain` — print the chain-of-custody log
Shows the full custody log recorded in `evidence/chain_of_custody.json`.

```bash
python scripts/forensics_toolkit.py chain
```

---

## Example: end-to-end workflow

```bash
# 1. Acquire: image the disk
python scripts/forensics_toolkit.py image --source /dev/sda --dest disk1.raw
sudo dd if=/dev/sda of=disk1.raw bs=4M conv=noerror,sync status=progress

# 2. Preserve: log custody + hash a suspicious artifact
python scripts/forensics_toolkit.py collect --path /tmp/suspicious.bin --handler "A. Analyst"

# 3. Analyze: disk (TSK) and memory (Volatility)
python scripts/forensics_toolkit.py tsk --image disk1.raw
python scripts/forensics_toolkit.py memory --file mem.raw

# 4. Report: review evidence and custody log
python scripts/forensics_toolkit.py chain
cat evidence/EVID-*/_report.json
```

---

## Tool reference

| Task | Tool | Example |
|------|------|---------|
| Disk imaging | FTK Imager / `dd` | `sudo dd if=/dev/sda of=disk1.raw bs=4M conv=noerror,sync` |
| File-system analysis | Sleuth Kit | `fls -r -p disk1.raw`, `fsstat disk1.raw`, `mmls disk1.raw` |
| GUI analysis | Autopsy | open the image / case in Autopsy |
| Memory capture | Volatility / memdump | create a `.raw` / `.mem` dump |
| Memory analysis | Volatility 3 | `vol3 -f mem.raw windows.malfind` |