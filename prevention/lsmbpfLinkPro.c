#include "vmlinux.h"          // kernel types (for CO-RE)
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include <linux/errno.h>

//license required
char LICENSE[] SEC("license") = "GPL"; //the license is a requirement for bpf verifier to let o>

extern int TARGET_GETDENTS_ID; //we will get here the id of this target that will match the ver>
extern int TARGET_SYS_BPF_ID;  //sane logic here (the python loader will get it for us)

//the program function definition:
//1) we precise the hook name in SEC
SEC("lsm/bpf_prog_load") //2)we define the hook of our lsm bpf: it must get called every time a>
int BPF_PROG(LinkProBPFMonitorSalma, struct bpf_prog *prog, u32 uflags)
{
    //get the target function ID and the program type
    u32 target_id = BPF_CORE_READ(prog, attach_btf_id); //these 2 fields are defined ,in kernel
    u32 prog_type = BPF_CORE_READ(prog, type);

    //First Check: is the program an LSM, or a kprobe/kretprobe
    if (prog_type == BPF_PROG_TYPE_LSM || prog_type == BPF_PROG_TYPE_KPROBE) {
        if (target_id == TARGET_GETDENTS_ID || target_id == TARGET_SYS_BPF_ID) { //if its trynn>
            bpf_printk("jokes on u LinkPro, no way u'll hook ur bpf to ID:%d", target_id);
            return -EPERM; //the loading of the bpf into the kernel is blocked
        }
    }

    return 0; //bpf is safe, the loading into kernel is allowed
}

