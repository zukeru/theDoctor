#!/usr/bin/python
import os
import time
from subprocess import Popen, PIPE

def shell_command_execute(command):
    p = Popen(command, stdout=PIPE, shell=True)
    (output, err) = p.communicate()
    return output

def update_repo():
    command = "cd %s; git fetch origin; git cherry master origin/master; " % os.getcwd()
    git_status = shell_command_execute(command)
    git_update = "failure"
    if git_status:
        command = "cd %s; git stash;" % os.getcwd()
        shell_command_execute(command)
        
        command = "cd %s; git reset origin master;" % os.getcwd()
        shell_command_execute(command)
        
        command = "cd %s; git pull; " % os.getcwd()
        git_update = shell_command_execute(command)
        
        if "Updating" in str(git_update):
            git_update = "success"
    
    if not git_update:
        git_update = 'None Needed'
        
    return [git_status,git_update]

def find_current_jobs():
    
    jobs_list = os.listdir("jobs/")
    job_dict = {}
     
    for filename in jobs_list:
        if filename.split('.')[1] != "cron" and "DS_Store" not in filename.split('.')[1]:
            #if the filename is the python script assume there is a cron and split and open the cron file to get the timing.#need to do the args parsing.
            try: 
                cron_args = None
                #open .cron file
                build_file_path = os.getcwd() + "/jobs/" + filename.split('.')[0] + ".cron"
                cron_lines = open(build_file_path)
                cron_timing = cron_lines.readlines()

                if len(cron_timing) > 1:
                    cron_args = cron_timing[1]

                if cron_args:
                    job_dict[filename.split('.')[0]] =  {"filename": filename, "cron_timing":cron_timing[0], "cron_args": cron_args}
                else:
                    job_dict[filename.split('.')[0]] =  {"filename": filename, "cron_timing":cron_timing[0], "cron_args": None}        
            except Exception as e:
                print e
    
    if not jobs_list:
        print "There are currently no jobs to schedule. I will continue on my mission until a job has arrived."   
    else:
        print "it has begun"
        update_jobs(job_dict)

def build_script_location(job_dict, job):
    
    if ".py" in job_dict[job]["filename"]:
        if job_dict[job]["cron_args"]:
            insert_line = job_dict[job]['cron_timing'].strip() + " " + "python " + os.getcwd() + "/" + job_dict[job]["filename"] + " " + job_dict[job]["cron_args"]
        else:
            insert_line = job_dict[job]['cron_timing'] + " " + "python " + os.getcwd() + "/" + job_dict[job]["filename"]
        return insert_line
    
    if ".sh" in job_dict[job]['filename']:
        if job_dict[job]["cron_args"]:
            insert_line = job_dict[job]['cron_timing'].strip() + " " + "python " + os.getcwd() + "/" + job_dict[job]["filename"] + " " + job_dict[job]["cron_args"]
        else:
            insert_line = job_dict[job]['cron_timing'] + " " + "python " + os.getcwd() + "/" + job_dict[job]["filename"]
        return insert_line
     
def update_jobs(job_dict):
    #specify the location of crontab, open the file and re-write with new information.
    cron_file_location = "/etc/crontab"
    cron_file = open(cron_file_location, "w")
    
    cron_file.write("SHELL=/bin/bash \n")
    cron_file.write("PATH=/sbin:/bin:/usr/sbin:/usr/bin \n")
    cron_file.write("MAILTO=root HOME=/ \n")
    for job in job_dict:
        insert_line = build_script_location(job_dict, job)
        print insert_line
        cron_file.write(insert_line)
    
    cron_file.close()
    
def main():
    first = True
    check_interval = 30
    
    while True:
        print "The doctor's tardis is in route."
        if first == True:
            #update repo first if there is a difference and replace cron jobs
            print "This is my first run so I will update my repo to the latest model."
            update_repo()
            print "I will now find all current jobs to schedule."
            find_current_jobs()
            print "I am going to sleep for " + str(check_interval)
            time.sleep(check_interval)
            first = False
        else:
            print "Look for changes to the jobs in the system, if found I will update to the latest model."
            status = update_repo() 
            if status[1] == 'success':
                print "Holy Bonkers, the Daliks are attacking.."
                #check the repo files
                find_current_jobs()
            print "I'm tired im going to sleep for " + str(check_interval)
            time.sleep(check_interval)            
    
if __name__ == '__main__': 
    
    main()
