#define _DEFAULT_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <ctype.h>
#include <err.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <execinfo.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/stat.h>
#include <sys/reg.h>
#include <sys/types.h>
#include <sys/ptrace.h>
#include <dlfcn.h>
#include <assert.h>
#include <libgen.h>

void
fault (const char* format, ...)
{
    static const int buff_len = 1024;
    int calls;
    char errbuff[buff_len];
    void *callbuff[buff_len];

    memset(errbuff, 0, buff_len);

    va_list args;
    va_start(args, format);
    vsnprintf(errbuff, buff_len, format, args);
    va_end(args);

    fprintf(stderr, "%s\n", errbuff);
    calls = backtrace(callbuff, buff_len);
    backtrace_symbols_fd(callbuff, calls, 2);
    exit(EXIT_FAILURE);
}

void
handle_child (char **argv)
{
    /* die when parent dies */
    prctl(PR_SET_PDEATHSIG, SIGHUP);
    ptrace(PTRACE_TRACEME, 0, NULL, NULL);
    char *envp[] = { "LD_BIND_NOW=1", NULL };
    /* doesn't return on success */
    execve(argv[0], argv, envp);
    fault("Child failed to run '%s': %s\n", argv[0], strerror(errno));
}

void
handle_parent (int pid, char **argv)
{
    struct user_regs_struct regs;
    char cmd[128];
    int status;

    waitpid(pid, &status, 0);
    if (!(WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP))
        fault("Child did not sync!\n");

    sprintf(cmd, "cat /proc/%d/maps", pid);
    system(cmd);

    while (1) {
        if (ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL) < 0)
            fault("Process did not step: %s", strerror(errno));

        waitpid(pid, &status, 0);
        if (!(WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP)) {
            if (WIFEXITED(status)) {
                if (WEXITSTATUS(status) == 0)
                    break;
                else
                    fault("Process exited with %d", WEXITSTATUS(status));
            }
            else if (WIFSTOPPED(status)) {
                siginfo_t siginfo;
                ptrace(PTRACE_GETSIGINFO, pid, 0, &siginfo);
                fault("Process stopped with %d at %p",
                        WSTOPSIG(status), siginfo.si_addr);
            }
        }

        if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) < 0)
            fault("Cannot read child registers: %s!\n", strerror(errno));
        printf("%llx\n", regs.rip);
        //fprintf(stderr, "%llx\n", regs.rip);
    }
}

int
main (int argc, char **argv)
{
    int pid;

    if (argc < 3)
        fault("Usage: %s <exe> [exe args...]\n", argv[0]);

    pid = fork();
    if (pid == 0)
        handle_child(argv + 1);
    else if (pid > 0)
        handle_parent(pid, argv);
    else
        fault("Fork failed: %s\n", strerror(errno));

    return 0;
}
