import libbpf
import subprocess  
import time

def get_btf_id(func_name):
    #this fct is what will get us the IDs of the 2 syscalls getdents and sys_bpf
    #for this we will use bpftool command to dump the file /sys/kernel/btf/vmlinux and find em
    cmd = f"bpftool btf dump file /sys/kernel/btf/vmlinux | grep 'FUNC' | grep ' {func_name}'"
    out = subprocess.check_output(cmd, shell=True).decode()
    #line looks like: [1234] FUNC '__x64_sys_getdents64' ...
    return int(out.split('[')[1].split(']')[0])
  

#we will store the IDs in these two variables
getdents_id = get_btf_id("__x64_sys_getdents64")
sys_bpf_id = get_btf_id("__x64_sys_bpf")


#our compiled bpf code using clang is now an ELF file
#we will open it WITHOUT loading it into kernel yet, because the "extern" variables are still m>
obj = libbpf.BpfObject.open("lsmbpfLinkPro.o")

#now its time for the Relocation Phase
#we will fill the 'extern' variables in the .bss section (when the compiler finds extern variab>
obj.bss.TARGET_GETDENTS_ID = getdents_id #the loader will look for the name TARGET_GETDENTS_TD,>
obj.bss.TARGET_SYS_BPF_ID = sys_bpf_id #same

#we move to THE KERNEL LOAD (The Verifier Phase)
#we can now push the object with the injected values to the kernel verifier
obj.load()

#THE ATTACHMENT
#we will find our specific LSM program by the name defined in the C code
program = obj.find_program_by_name("LinkProBPFmonitorSalma")
program.attach() #we attach it to the specified hook

#if we want our bpf to stay alive , then loader must stay alive:
try:
    while True:
        # Keep script alive to maintain the hook
        time.sleep(1)
except KeyboardInterrupt:
    print("our security policy is dying")

