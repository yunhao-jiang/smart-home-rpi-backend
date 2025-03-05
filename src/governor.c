// Energy-efficient real time scheduler
// Important! DO NOT MODIFY this file. You will not submit this file.
// This file is provided for your implementation of the program procedure.
// For more details, please see the instructions in the class website.

#include "governor.h"
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <string.h>
#include <assert.h>

#define SETFREQ_SYSCALL_NUM 442

static int maxFreq = 0;
static int minFreq = 0;
static int curFreq = 0;

#define POLICY_PATH "/sys/devices/system/cpu/cpufreq/policy0/"

void init_userspace_governor() {
	char buf[32];

	FILE* fp;
	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "w");
	fprintf(fp, "userspace");
	fclose(fp);


	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", "r");
	fscanf(fp, "%d", &maxFreq);
	fclose(fp);

	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq", "r");
	fscanf(fp, "%d", &minFreq);
	fclose(fp);

	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed", "r");
	fscanf(fp, "%d", &curFreq);
	fclose(fp);

	// Custom syscall test:
	// Instead of File IO, we use a custom system call to minimize FILE IO time.
	// Here, we test if it correctly works in the custom kernel.
	set_by_min_freq();

	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r");
	fscanf(fp, "%d", &curFreq);
	fclose(fp);

	printf("MIN frequency change test: %d == %d\n", curFreq, minFreq);


	set_by_max_freq();

	fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r");
	fscanf(fp, "%d", &curFreq);
	fclose(fp);

	printf("MAX frequency change test: %d == %d\n", curFreq, maxFreq);
}

int write_driver(const char *fullpath, const char *data) {
    int fdd = open(fullpath, O_WRONLY | O_CLOEXEC);
    if (fdd < 0)
        return -1;
    if (write(fdd, data, strlen(data)) < 0) {
        close(fdd);
        return -1;
    }
    close(fdd);
    return 0;
}

static void set_governor(const char* szNewGovernor) {
	FILE* fp;
	fp = fopen(POLICY_PATH"scaling_governor", "w");
	fprintf(fp, "%s", szNewGovernor);
	fclose(fp);
}

static void read_freq() {
	FILE* fp;
    fp = fopen(POLICY_PATH"scaling_max_freq", "r");
	fscanf(fp, "%d", &maxFreq);
	fclose(fp);

    fp = fopen(POLICY_PATH"scaling_min_freq", "r");
	fscanf(fp, "%d", &minFreq);
	fclose(fp);
}

void set_userspace_governor() {
    set_governor("userspace");
    if (maxFreq == 0)
        read_freq();
}


void set_ondemand_governor() {
    set_governor("ondemand");
    if (maxFreq == 0)
        read_freq();
}


static void set_frequency(int frequency) {
	FILE* fp;
	fp = fopen(POLICY_PATH"scaling_setspeed", "w");
	fprintf(fp, "%d", frequency);
	fclose(fp);
}

void set_by_max_freq() {
    assert(maxFreq > 0);
	set_frequency(maxFreq);
}


void set_by_min_freq() {
    assert(minFreq > 0);
	set_frequency(minFreq);
}

int get_cur_freq() {
	int curFreq;
	FILE* fp = fopen(POLICY_PATH"scaling_setspeed", "r");
	fscanf(fp, "%d", &curFreq);
	fclose(fp);

	return curFreq;
}