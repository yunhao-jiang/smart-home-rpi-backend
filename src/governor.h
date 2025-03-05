// Week 4: Energy-efficient real time scheduler
// Important! DO NOT MODIFY this file. You will not submit this file.
// This file is provided for your implementation of the program procedure.
// For more details, please see the instructions in the class website.

#ifndef _GOVERNOR_H_
#define _GOVERNOR_H_

// Assume single core use
void init_userspace_governor();
int write_driver(const char*, const char*);
void set_by_max_freq();
void set_by_min_freq();
int get_cur_freq();

void set_userspace_governor();
void set_ondemand_governor();

#endif