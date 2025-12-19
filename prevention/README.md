# Prevention Attempt: eBPF LSM
This directory contains an experimental prevention idea inspired by the LinkPro rootkit.
## Goal
Block eBPF programs that attempt to hook visibility-related syscalls such as:`getdents*` and `sys_bpf` before they are loaded into the kernel.
## Approach
-Attach an eBPF program to the `lsm/bpf_prog_load` hook, inspect the intent of the program being loaded, deny loading if it targets sensitive visibility paths
## Limitation Encountered
The kernel does not expose internal fields of `struct bpf_prog` to eBPF programs via BTF.
As a result:
Program type and attach target cannot be introspected. CO-RE relocation cannot resolve required fields. The policy cannot be enforced as written.

This is a **deliberate kernel security design choice**, not a bug. Further work could be done later to overcome it.
