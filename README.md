# LinkPro eBPF Rootkit: Analysis & Prevention Attempt

This repository documents a dive into **LinkPro**, a real world eBPF based rootkit observed in attacks against AWS and Linux environments.

The goal of this is not to provide a production-ready defense, but to:
- understand how modern eBPF rootkits operate,
- visualize their execution flow,
- and explore where kernel-level prevention is technically possible,and where it is not.


## Contents

- `article/` : Detailed technical analysis of the LinkPro attack chain
- `diagrams/` : Static and interactive diagrams explaining the runtime behavior
- `prevention/` : An experimental eBPF LSM-based prevention idea + explanation article
- `references/` : Public sources and research used


## What this project covers

- Jenkins CVE exploitation and container escape
- Abuse of eBPF kretprobes on sensitive syscalls
- Post-syscall userspace buffer tampering (`getdents*`)
- Fallback persistence using `LD_PRELOAD`
- Passive C2 activation using XDP / TC (magic packet)
- Limitations of kernel introspection for security enforcement


## Prevention experiment (important note)

The prevention code in this repository represents an **exploration**, not a finished solution.

It attempts to use an **eBPF LSM hook** to block suspicious eBPF programs at load time, inspired by LinkPro-style attacks.

Due to deliberate kernel design constraints (opaque `struct bpf_prog`), this policy cannot be fully enforced on current kernels.

This limitation is explained in detail in `prevention/README.md`.


## Why this repo exists

This project helped me understand that:
- eBPF security is constrained by what the kernel exposes,
- prevention is not just about ideas, but about enforcement boundaries,
- and understanding these limits is a core skill in low-level security work.
and of course deepen a lot more my initial knowledge on BPF.

## Disclaimer

This repository is for **educational purposes only**.
