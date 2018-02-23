import re
import csv
import os
import os.path
import time, datetime
from fabric.api import *
#from fabric.api import settings, abort



env.hosts = ['192.168.1.30']
# Set the username
env.user   = "root"
# Set the password [NOT RECOMMENDED]
env.password = "test0000"

tools_folder_location = os.getcwd() + "/tools"
print "tools_folder_location is: ", tools_folder_location
result_csv_file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') +"_result.csv"
#creating result csv file
with open(result_csv_file_name, 'w') as csvfile:
        fieldnames = ['Test_Name', 'Test_Result', 'Comments or Errors']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #if not os.path.isfile("result.csv"):
    	writer.writeheader()

#test_case: mprime_automation for cpu mode test
def mprime_automation():
    test_name = "turbo_mode_test"
    return_message = ""
    result = "FAIL"
    put(tools_folder_location + "/mprime_v29.3", "/usr/local/bin/mprime")
    enabling_executable_option = run_command_with_warn_only_true("chmod 755 /usr/local/bin/mprime")		
    print "Now will run mprime stress"
    print "while mprime is running, will start turbostat to capture cstate residency and cpu frequency"
    #running any command in background with ssh will get killed as soon as we exit out of ssh. So the best way to run any command in background using ssh is to run the next command in parallel and wait for the exist status of the second command to go to next step. This will avoid use case of nohup and screen like implementation which might or might not work.
    #mprime_async_cmd_output = run_command_with_warn_only_true("mprime -t > /dev/null 2>&1 &")
    mprime_async_cmd_output = run_command_with_warn_only_true("mprime -t & timeout 40s turbostat -i 1 | tee /tmp/turbostat_output_with_mprime.txt")
    
    print "Will kill mprime and then capture turbostat log"
    mprime_pid_output = run_command_with_warn_only_true("sudo pkill mprime")
    turbostat_cmd_output = run_command_with_warn_only_true("timeout 40s turbostat -i 1 | tee /tmp/turbostat_output_without_mprime.txt")
    
    return_message = "mprime test over"
    print return_message
    if mprime_async_cmd_output.failed:
        result = "FAIL"
	print "FAIL"
    else:
	result = "PASS"	
	print "PASS"
    
    print return_message
    return (test_name, result, return_message)

 
def batch_run():
    run_test(turbo_mode_test)

	
#basic functions which will help write test scripts.

def run_command_with_warn_only_true(cmd):
    with settings(warn_only=True):
        return run(cmd)

# Writing test_result into csv file
def write_test_result_into_csv(result_csv_file_name, test_name, test_result, message):
    with open(result_csv_file_name, 'a') as csvfile:
        fieldnames = ['Test_Name', 'Test_Result', 'Comments or Errors']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'Test_Name': test_name, 'Test_Result': test_result, 'Comments or Errors': message})

def run_test(test_method_name):
    test_result = test_method_name()
    print "test_result is******************", test_result
    write_test_result_into_csv(result_csv_file_name, test_result[0], test_result[1], test_result[2])

    
    

