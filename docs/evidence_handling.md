# Evidence Handling Standard

## Principles (NIST SP 800-86 / SWGDE)
1. **Preserve integrity** – hash everything, work only on copies.
2. **Document everything** – who touched the evidence, when, why.
3. **Minimize alteration** – do not install tools or reboot a live suspect system
   before imaging memory.
4. **Maintain chain of custody** – a continuous record of possession from
   collection to court presentation.

## Do's
- Power on / image memory **first**, disk **second**.
- Use write-blockers on source disks.
- Compute SHA-256 of every image and artifact.
- Store evidence on dedicated, sealed media.
- Log each transfer with a signed, timestamped entry.

## Don'ts
- Don't run `chkdsk`, `fsck`, or "repair" tools on source media.
- Don't boot the suspect OS normally before imaging.
- Don't analyze the original – use a verified copy.
- Don't take unrecorded actions that alter timestamps (access time).

## Evidence acquisition order (live system)
1. Live memory (Volatility / WinPmem / FTK Imager memory mode)
2. Running processes and network state
3. Disk image
4. Peripheral/removable media
