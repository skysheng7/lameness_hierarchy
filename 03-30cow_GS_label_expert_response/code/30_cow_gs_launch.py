"""
###############################################################################
###############################################################################
###                                                                         ###
### Author: Kehan (Sky) Sheng                                               ###
### Email: skysheng7@gmail.com                                              ###
### Association: UBC                                                        ###
### Date: September 12 2020 -  July 18, 2021                                ###
### Location: Vancouver, BC, Canada                                         ###
###                                                                         ###
### Description:  This code changes file name for the Amazon MTurk project, ###
###               trasnfer video formats and merge multiple video clips into###
###               one. This code also allow you to connect to Amazon AWS    ###
###               directly and use its developer API. We create HITs,       ###
###               approve worker's submittion, and collect response results ###
###               using Python code directly.                               ###
###                                                                         ###
### Source: 		  (1) 2017 Amazon.com, Inc.: CreateHitSample.py         ###
###                 file:///Users/skysheng/Downloads/CreateHitSample.py.html###
###                                                                         ###
###############################################################################
###############################################################################
"""

#import the packages
import os
import glob
import pandas as pd
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import random
import re
import boto3
import sys
import csv
import numpy as np
import xmltodict
from datetime import date
import datetime
import json
import math


# get today's date
today = date.today().strftime("%b-%d-%Y")
envir = "Sky"
if (envir == "Sky"):
    input_dir = "/Users/skysheng/Library/CloudStorage/OneDrive-UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/results/gs_labeling_html"
    key_dir ='/Users/skysheng/Library/CloudStorage/OneDrive-UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/data/Amazon MTurk'
    output_dir = "/Users/skysheng/Library/CloudStorage/OneDrive-UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/results/30_cow_gs_HIT_launch"
    #output_dir = '/Users/skysheng/Library/CloudStorage/OneDrive-UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/Sora Jeong/results/Amazon MTurk expert response'
"""
###############################################################################
######################## Connect to Amazon AWS API ############################
###############################################################################
"""

""" 
Connect to Amazon AWS using access key
"""

def create_mturk_client(create_hits_in_live, key_dir):
    # Load the access key credential file
    os.chdir(key_dir)
    access_key = pd.read_csv("awp_rootkey.csv", header=None)
    access_key_id_raw = access_key.at[0, 0]
    access_key_key_raw = access_key.at[1, 0]

    # Specify region name and access key to Amazon AWS account
    region_name = 'us-east-1'
    aws_access_key_id = access_key_id_raw.split("=")[1]
    aws_secret_access_key = access_key_key_raw.split("=")[1]
    
    environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
        },
    }
        
    mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]
    


    client = boto3.client(
        service_name='mturk',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=mturk_environment['endpoint'],
    )

    return client, mturk_environment


def initialize_mturk_client(create_hits_in_live, html_name, cur_HIT_num, max_worker_num, key_dir):
    # Set the number of questions
    if cur_HIT_num == 0:
        num_questions = 30
    else:
        num_questions = 30
    award_value = num_questions / 10

    # Use profile if one was passed as an arg, otherwise
    profile_name = sys.argv[1] if len(sys.argv) >= 2 else None
    session = boto3.Session(profile_name=profile_name)
    
    # Create a client
    client, mturk_environment = create_mturk_client(create_hits_in_live, key_dir)

    # Test that you can connect to the API by checking your account balance
    user_balance = client.get_account_balance()
    # In Sandbox this always returns $10,000. In live, it will be your actual balance.
    print("Your account balance is {}".format(user_balance['AvailableBalance']))

    mturk_environment['reward'] = str(award_value)
    return client, mturk_environment



"""
###############################################################################
################################ Create HITs ##################################
###############################################################################
"""

def create_and_submit_hit(client, input_dir, html_name, mturk_environment, max_worker_num, num_questions, cur_HIT_num):
    today = date.today().strftime("%b-%d-%Y")
    os.chdir(input_dir)
    question_sample = open((html_name), "r").read()


    #TODO: change the master worker ID qualifacation once in live!!!!
    # Master's qualification ID in sandbox: 2ARFPLSP75KLA8M8DH1HTEQVJT3SY6 : 
    # this means we want master workers (high performance workers)
    #Worker_​PercentAssignmentsApproved ID: 000000000000000000L0
    worker_requirements = [{
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [0],  # we only want workers with >= 80% approval rate in the past
        'RequiredToPreview': True,
    }]

    response = client.create_hit(
        MaxAssignments=max_worker_num,  #MaxAssignments: how many Workers you want to work on this 
        LifetimeInSeconds=2592000, # 30days # How long this HIT will show up on the market
        AssignmentDurationInSeconds=3600, # 1 h # How long we allow the worker to work on one assignment
        AutoApprovalDelayInSeconds=1209600, # 14 days # How long to auto approve if we did not click approve ourselves
        Reward=mturk_environment['reward'],
        Title='Require PC/tablet/laptop: What is the gait score of the cow? (' + str(num_questions) + ' questions) HIT' +  str(cur_HIT_num) + ' ' + str(today),
        Keywords='cow, video, agriculture, animal, lameness',
        Description='Play two videos of cows walking side by side, and enter the gait score of each cow on 5 level scale.',
        Question=question_sample,
        QualificationRequirements=worker_requirements,
    )

    # Get the preview of HIT and the result
    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    hit_address = str(mturk_environment['preview'] + "?groupId={}".format(hit_type_id))
    result_address = str(mturk_environment['manage'])

    print("\nCreated HIT: {}".format(hit_id))
    print("\nYou can work the HIT here:")
    print(mturk_environment['preview'] + "?groupId={}".format(hit_type_id))
    print("\nAnd see results here:")
    print(mturk_environment['manage'])
    
    # Record the HIT address, and detailed information into a datasheet: submitted_tasks_tracker
    new_row = [{'HIT': cur_HIT_num, 'HIT_id': hit_id, 'HIT_website_address': hit_address, 'HIT_results_address': result_address}]
    submitted_tasks_tracker = pd.DataFrame(new_row)

    return submitted_tasks_tracker



def load_answer_key(input_dir, html_name):
    os.chdir(input_dir)
    HIT_answer = pd.read_csv(html_name + "_answer.csv")
    HIT_answer2 = HIT_answer[["GS_dif", "question_type", "question_num"]]
    return HIT_answer2

def process_html_files(html_files, input_dir, create_hits_in_live, key_dir, max_worker_num):
    master_submitted_tasks_tracker = pd.DataFrame()

    for html_file in html_files:
        #if html_file == "HIT0.html":
        #    continue

        html_name, cur_HIT_num = extract_hit_details(html_file)

        num_questions = set_num_questions(cur_HIT_num)
        award_value = num_questions / 10

        client, mturk_environment = initialize_mturk_client(create_hits_in_live, html_name, cur_HIT_num, max_worker_num, key_dir)

        submitted_tasks_tracker = create_and_submit_hit(client, input_dir, html_name, mturk_environment, max_worker_num, num_questions, cur_HIT_num)

        master_submitted_tasks_tracker = pd.concat([master_submitted_tasks_tracker, submitted_tasks_tracker], ignore_index=True)

    return master_submitted_tasks_tracker

def extract_hit_details(html_file):
    match = re.search(r'HIT(\d+)', html_file)

    if match:
        html_name = html_file # This will contain the whole match, 'HIT' + number
        cur_HIT_num = int(match.group(1))  # This will contain only the number part
        return html_name, cur_HIT_num
    return None, None


def set_num_questions(cur_HIT_num):
    if cur_HIT_num == 0:
        return 30
    else:
        return 30


# By default, HITs are created in the free-to-use Sandbox
create_hits_in_live = False
#create_hits_in_live = True
track_ip = False
max_worker_num = 20
#html_files = sorted(filter(lambda f: f.endswith(".html"), os.listdir(input_dir)))
html_files = ['GS_30cows_HIT0_Jun-04-2023.html']
master_submitted_tasks_tracker = process_html_files(html_files, input_dir, create_hits_in_live, key_dir, max_worker_num)
master_submitted_tasks_tracker = master_submitted_tasks_tracker.sort_values(by='HIT').reset_index(drop=True)

os.chdir(output_dir)
master_submitted_tasks_tracker.to_csv('all_submitted_tracker' + today + '.csv')

# a for loop to print out the HIT address of all HITs in master_submitted_tasks_tracker, in the format of "HIT0: address"
for index, row in master_submitted_tasks_tracker.iterrows():
    cur_HIT_num = row['HIT']
    hit_address = row['HIT_website_address']
    print("HIT" + str(cur_HIT_num) + ": " + hit_address)


"""
###############################################################################
########################## Collect Worker Response ############################
###############################################################################
"""
def all_q_columns(num_questions):
    return [f"q{i}" for i in range(1, num_questions + 1)]

def process_responses(response, worker_response_tracker, cur_HIT_num, hit_id, hit_address, result_address, hit_status, q_col, track_ip, client):
    
    # get the answer from the worker's response which is in XML format
    assignments = response['Assignments']
    
    # extract worker's response from XML format 
    if response['NumResults'] > 0:
        worker_response_tracker = extract_answer(assignments, cur_HIT_num, hit_id, hit_address, result_address, hit_status, worker_response_tracker, q_col)
     
    # iterate through each worker and score them
    for index in range(len(worker_response_tracker)):
        response_row = worker_response_tracker.iloc[[index]].copy()
        assignment_id = response_row.loc[response_row.index[0], 'Assignment_id']
        assignment_status = response_row.loc[response_row.index[0], 'assignment_status']

        if (assignment_status == "Submitted"):
                # Approve the assignment
                client.approve_assignment(
                    AssignmentId=assignment_id,
                    RequesterFeedback="Your submission has been approved. Thank you for your work!",
                )      
    return worker_response_tracker


def extract_answer(assignments, cur_HIT_num, hit_id, hit_address, result_address, hit_status, worker_response_tracker, q_col):

    submitted_num = len(assignments)
    
    for assignment in assignments:
        worker_id = assignment['WorkerId']
        assignment_id = assignment['AssignmentId']
        assignment_status = assignment['AssignmentStatus']
        answer_xml = parseString(assignment['Answer'])
        accept_time = assignment['AcceptTime']
        Submit_Time = assignment['SubmitTime']

        # the answer is an xml document. we pull out the value of the first
        # //QuestionFormAnswers/Answer/FreeText
        answer_js = answer_xml.getElementsByTagName('FreeText')[0]
        # See https://stackoverflow.com/questions/317413
        only_answer = " ".join(t.nodeValue for t in answer_js.childNodes if t.nodeType == t.TEXT_NODE)
        # load the JSON string as a pythoon object
        json_answer = json.loads(only_answer)
        # Extract the worker's IP address from the answer XML
        worker_ip_bot = json_answer[0].pop("worker_ip", None)
        json_answer_dict = json_answer[0].copy()
        if worker_ip_bot is not None:
            parts = worker_ip_bot.split("-");
            worker_ip = parts[0];
            isBot = parts[1];
        else:
            worker_ip = None
            isBot = None
        
        # Make a copy of the dictionary inside the list
        

        #print('The Worker with ID {} submitted assignment {} and gave the answer "{}"'.format(worker_id, assignment_id, only_answer))

        # Create a new row for the worker_response_tracker DataFrame
        new_row = {
            'HIT': cur_HIT_num,
            'HIT_id': hit_id,
            'HIT_website_address': hit_address,
            'HIT_results_address': result_address,
            'HIT_status': hit_status,
            'submitted_assignments': submitted_num,
            'Worker_id': worker_id,
            'Assignment_id': assignment_id,
            'Accept_time': accept_time,
            'Submit_time': Submit_Time,
            'Full_response': only_answer,
            'worker_ip': worker_ip,
            'isBot': isBot,
            'assignment_status': assignment_status
        }
        
        
        # Extract the true answers
        true_answers = {}
        for question, answers in json_answer_dict.items():
            for answer, value in answers.items():
                if value:
                    true_answers[question] = answer
        
        # Update the new_row with the true answers
        new_row.update(true_answers)
        
        # Convert the new_row dictionary to a DataFrame
        new_row_sheet = pd.DataFrame([new_row], columns=(['HIT', 'HIT_id', 'HIT_website_address', 'HIT_results_address', 'HIT_status', 'submitted_assignments', 'Worker_id', 'Assignment_id', 'Accept_time', 'Submit_time', 'Full_response', 'worker_ip', 'isBot','assignment_status'] + q_col))
        
        worker_response_tracker = pd.concat([worker_response_tracker,new_row_sheet], ignore_index=True)
        
    return worker_response_tracker


# read in submitted tasks
os.chdir(output_dir)
master_submitted_tasks_tracker = pd.read_csv("all_submitted_trackerAug-30-2023.csv")  

# Create a client
client, mturk_environment = create_mturk_client(create_hits_in_live, key_dir)

# create master dataframes to store all the responses from all HITs
master_worker_response_tracker = pd.DataFrame()

# iterate through all HITs
for index, row in master_submitted_tasks_tracker.iterrows():
    hit_id = row['HIT_id']
    cur_HIT_num = row['HIT']
    hit_address = row['HIT_website_address']
    result_address = row['HIT_results_address']
    html_name = "HIT" + str(cur_HIT_num)   
    os.chdir(input_dir)
    # Set the number of questions, there are 12 question sin HIT0, but the others have 10
    if (cur_HIT_num == 0):
        num_questions = 30
    else:
        num_questions = 30
        
        
    print(html_name)
        
    # Get the status of the current HIT
    hit = client.get_hit(HITId=hit_id)
    hit_status = str(hit['HIT']['HITStatus'])
    # get a dictionary with worker's response
    response = client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=['Submitted', 'Approved', 'Rejected'],
            #AssignmentStatuses=['Submitted'],
            MaxResults=100,
            )
    
    # Process worker responses
    q_col = all_q_columns(num_questions)
    worker_response_tracker_columns = ['HIT','HIT_id','HIT_website_address','HIT_results_address', 'HIT_status', 'submitted_assignments', 'Worker_id', 'Assignment_id', 'Accept_time', 'Submit_time', 'Full_response', 'worker_ip','isBot','assignment_status'] + q_col
    
    # create a datasheet to record workers' responses
    worker_response_tracker = pd.DataFrame(columns=worker_response_tracker_columns)
    # process responses
    worker_response_tracker = process_responses(response, worker_response_tracker, cur_HIT_num, hit_id, hit_address, result_address, hit_status, q_col, track_ip, client)
    
    # Update the master DataFrames
    master_worker_response_tracker = pd.concat([master_worker_response_tracker, worker_response_tracker], ignore_index=True)

# assign round number
master_worker_response_tracker[["GS_round"]] = 3
# Save DataFrames to CSV files
os.chdir(output_dir)
master_worker_response_tracker.to_csv('master_worker_response_tracker_Anna-merick' + today + '.csv', index=False)


"""
###############################################################################
########################## Monitor HIT status ############################
###############################################################################
"""


# iterate through all 53 HITs, monitor how many HITs were submitted
for index, row in master_submitted_tasks_tracker.iterrows():
    hit_id = row['HIT_id']
    cur_HIT_num = row['HIT']
    hit_address = row['HIT_website_address']
    result_address = row['HIT_results_address']
    html_name = "HIT" + str(cur_HIT_num)   
    # Set the number of questions, there are 12 question sin HIT0, but the others have 10
    if (cur_HIT_num == 0):
        num_questions = 30
    else:
        num_questions = 30
        
        
    # Get the status of the current HIT
    #hit = client.get_hit(HITId=hit_id)
    #hit_status = str(hit['HIT']['HITStatus'])
    
    # get a dictionary with worker's response
    response = client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=['Submitted', 'Approved', 'Rejected'],
            #AssignmentStatuses=['Submitted'],
            MaxResults=100,
            )
    
    print(hit_id)
    print(html_name + ": Submitted " + str(response['NumResults']))



"""
###############################################################################
################### Collect Expert Response from csv ##########################
###############################################################################
"""

def extract_answer_manual(hit_num, expert, html_name, full_rp, worker_response_tracker):

    # load the JSON string as a pythoon object
    full_rp = full_rp.replace("\n", "")
    json_answer = json.loads(full_rp)
    # Extract the worker's IP address from the answer XML
    worker_ip_bot = json_answer[0].pop("worker_ip", None)
    json_answer_dict = json_answer[0].copy()
    if worker_ip_bot is not None:
        parts = worker_ip_bot.split("-");
        worker_ip = parts[0];
        isBot = parts[1];
    else:
        worker_ip = None
        isBot = None

    # Create a new row for the worker_response_tracker DataFrame
    new_row = {
        'HIT': hit_num,
        'Worker_id': expert,
        'html': html_name,
        'Full_response': full_rp,
    }
    
    
    # Extract the true answers
    true_answers = {}
    for question, answers in json_answer_dict.items():
        for answer, value in answers.items():
            if value:
                true_answers[question] = answer
    
    # Update the new_row with the true answers
    new_row.update(true_answers)
    
    # Convert the new_row dictionary to a DataFrame
    new_row_sheet = pd.DataFrame([new_row], columns=(['HIT', 'Worker_id', 'html', 'Full_response'] + q_col))
    
    worker_response_tracker = pd.concat([worker_response_tracker,new_row_sheet], ignore_index=True)
    
    return worker_response_tracker


os.chdir(output_dir)
manual_rp = pd.read_csv("gs_expert_manual_response.csv")
manual_rp = manual_rp[['Expert', 'Response', 'html', 'date', 'GS_round']]
manual_rp.dropna(inplace=True)


# create master dataframes to store all the responses from all HITs
master_worker_response_tracker = pd.DataFrame()
num_questions = 30
hit_num = 0

# iterate through all HITs
for index, row in manual_rp.iterrows():
    expert = row['Expert']
    html_name = row['html']
    full_rp = row['Response']
    gs_round = row['GS_round']
    
    # Process worker responses
    q_col = all_q_columns(num_questions)
    worker_response_tracker_columns = ['HIT', 'Worker_id', 'html', 'Full_response'] + q_col
    
    # create a datasheet to record workers' responses
    worker_response_tracker = pd.DataFrame(columns=worker_response_tracker_columns)
    # process responses
    worker_response_tracker = extract_answer_manual(hit_num, expert, html_name, full_rp, worker_response_tracker)
    worker_response_tracker[["GS_round"]] = gs_round
    
    # Update the master DataFrames
    master_worker_response_tracker = pd.concat([master_worker_response_tracker, worker_response_tracker], ignore_index=True)


# Save DataFrames to CSV files
os.chdir(output_dir)
master_worker_response_tracker.to_csv('manual_expert_response_extract_' + today + '.csv', index=False)

