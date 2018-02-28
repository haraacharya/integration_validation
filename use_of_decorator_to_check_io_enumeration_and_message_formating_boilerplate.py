import re
import csv
import os
import os.path
import time, datetime
from fabric.api import *
from functools import wraps



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
        if not os.path.isfile("result.csv"):
    	    writer.writeheader()

#example use of decorators
def device_check(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        lspci_check_before_test = run_command_with_warn_only_true("lspci | wc -l")
	#sample command output if you want to convert to integer for further operation
        lspci_check_before_test_after_format = command_output_formatter(lspci_check_before_test)
	print "lspci_check_before_test_after_format in int is:", int(lspci_check_before_test_after_format)
	print type(lspci_check_before_test), lspci_check_before_test
	print "lspci_check_before_test is: ", lspci_check_before_test
        r = f(*args, **kwargs)
        if run_command_with_warn_only_true("lspci | wc -l") != lspci_check_before_test: 
	    print "****************************************lspci check before and after test FAILED****************************************"
        else:
	    print "****************************************lspci check before and after test PASSED****************************************"
	return r
    return wrapped

@device_check
def verify_memory_type():
	test_name = "verify_memory_type"
	return_message = ""
	result = "FAIL"
	with settings(warn_only=True):
		run_command_with_warn_only_true("sync")
	result = run_command_with_warn_only_true("cat /sys/firmware/log | grep -i lpddr")
        new_result = return_message_formatter(result)
	
        print "stdout is:********", new_result, "****************************"
	if result.find("LPDDR"):
		print "The LPDDR is present"
		return_message = new_result
		result = "PASS"
	else:
		print "The LPDDR is not present"
		return_message = "LPDDR is not present"
		result = "FAIL"
	return (test_name, result, return_message)

 
def batch_run():
    run_test(verify_memory_type)

	
#basic functions which will help write test scripts.

#formating the return message in fabric as the fabric return values might contain ansi escape sequences
def return_message_formatter(message):
    ansi_escape_regex = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    new_message = ansi_escape_regex.sub('', message)
    newline_escape = re.compile(r'\r\n')
    new_message = newline_escape.sub(', ', new_message)
    return new_message	

def command_output_formatter(message):
    ansi_escape_regex = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    new_message = ansi_escape_regex.sub('', message)
    new_message = new_message.strip()
    newline_escape = re.compile(r'\r\n')
    new_message = newline_escape.sub('', new_message)
    return new_message

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

    
    

