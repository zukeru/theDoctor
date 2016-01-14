import os
import datetime
os.mkdir("~/job_test_tmp_files")
dt_file_location = "~/job_test_tmp_files/"+str(datetime.datetime.now())
dt_file = open(cron_file_location, "w")
dt_file.write("The Daliks are Attacking.")
dt_file.close()