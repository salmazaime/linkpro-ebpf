LinkPro: That Sneaky eBPF Rootkit Hitting AWS and Linux Servers

Everything kicked off with a vulnerable Jenkins server left exposed. Jenkins is basically this open-source tool for automating software builds, tests, deployments, all that CI/CD stuff. In this case, the attackers exploited CVE 2024-23897 to push a malicious Docker image (called kvlnt/vv) into AWS EKS clusters.

Inside that image, there was a Rust program called vGet, a downloader. Downloaders are sneaky programs because they often pretend to be something harmless (like a software update, a free game, or even just running quietly after you open a bad email attachment or visit a shady site). But once they're in, their real job is to fetch the dangerous stuff: ransomware, spy tools, or in this attack, rootkits that burrow deep into the system.

vGet grabbed an encrypted payload from an AWS S3 bucket, that turned out to be VShell (an open-source backdoor for remote control). VShell sets up a connection to the attacker's C2 server, and thanks to some bad container configs (like host filesystem mounts that let it reach outside), the hackers escaped the container, grabbed root access on the actual host, and started jumping between EKS clusters to spread further.

From there, using VShell's remote access, they dropped the main star: LinkPro, a Golang rootkit. It packs a few ELF files inside: a shared library (libld.so), two eBPF programs (called Hide and Knock by the researchers, probably descriptive names, not sure if the attackers labeled them that way), and an extra unused kernel module (arp_diag.ko). That's why disabling unused kernel modules is good security: if nothing needs it, turn it off to shrink the attack surface.

The Hide part does exactly what you'd guess: it hides the attacker's traces. It uses tracepoints and kretprobes (these are eBPF hooks) on syscalls like getdents() (that's the syscall behind commands like ls, which fills a userspace buffer with directory listings). And it also hooks sys_bpf to hide its own eBPF stuff from tools like bpftool.

Important bit here: eBPF doesn't sit in the middle blocking copies from kernel to userspace. The timeline goes like this:

1. Userspace calls getdents()
2. Kernel does its thing and copies the full directory info into the userspace buffer
3. Then the eBPF kretprobe kicks in, only now
4. Syscall returns the (possibly tampered) buffer to the program

So the eBPF code just tweaks the buffer in userspace after the kernel's done its honest work. It filters out bad files, processes, or its own maps right before you see them. Super sneaky post-processing.

If eBPF isn't available (kernel restrictions or whatever), LinkPro has a backup: it drops “libld.so” and adds it to “/etc/ld.so.preload”. That forces the library to load first in most programs. Then it hooks libc functions like getdents(), getdents64(), readdir(), even syscall() sometimes. The fake versions call the real ones, remove anything suspicious from the results, and hand back the cleaned up list.

This fallback isn't perfect though cause static binaries (where everything's baked in at compile time) ignore LD_PRELOAD, and some processes might not pick it up.

Now the "Knock" part. This handles the passive C2 mode, like a hidden listener waiting for a signal. It watches for a "magic packet": a TCP SYN with window size exactly 54321. (Not the full Wake-on-LAN style with MAC repeats, more like a custom port-knock trick using XDP and TC eBPF programs to catch and redirect packets early.)

When it spots one, it notes the sender's IP, opens a one-hour window, and redirects traffic from whatever front-end port the attacker picks to its internal listener on port 2233 (rewriting headers so logs don't match up easily). Only that specific traffic gets forwarded, everything else passes normally, so no big disruptions that would raise alarms. Smart way to bypass firewalls without opening everything wide.

Once activated, LinkPro gives the attacker a full remote shell, file browsing/uploading/downloading, even SOCKS5 proxy for pivoting. It can use DNS or HTTP for C2 too.

For staying around after reboots, LinkPro pretends to be systemd-resolved (the legitimate DNS resolver service). It drops the binary at “/usr/lib/.system/.tmp~data.resolveld” (timestamps faked to match real files), and creates a fake service file “/etc/systemd/system/systemd-resolveld.service”.
