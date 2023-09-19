import pandas as pd
import numpy as np
import math
import os

exec(open("pairwise_further_processing_helper.py").read())

"""
###############################################################################
###### convert individual expert pairwise response to winner loser df #########
###############################################################################
"""
# load all reponse and answer key csv
expert_response_dir = "../results/all_experts"
answer_dir1 = "../../04-generate_54HIT_html_experts/results"
answer_dir2 = "../results/wali_resubmission_html"
data_path_1='all_HIT_answer.csv'
data_path_2='master_all_responses_May-14-2023_to_May-18-2023_Dan.csv'

df_1= pd.read_csv(os.path.join(answer_dir1, data_path_1))
column_ord = ['cow_L', 'cow_R', 'cow_L_URL', 'cow_R_URL', 'cow_L_GS', 'cow_R_GS', 'GS_dif', 'question_type', 'question_num', 'HIT', 'question_id', 'pair_id']
#df_1 = merge_csv_files(df_1, answer_dir2, column_ord)

df_2= pd.read_csv(os.path.join(expert_response_dir, data_path_2))

final_df = process_and_merge(df_1, df_2)
final_df[["expert"]] = "DW"
winner_loser_df = create_winner_loser_degree_df(final_df)
winner_loser_df[["expert"]] = "DW"

winner_loser_df.to_csv(os.path.join(expert_response_dir, 'winner_loser_Wali.csv'), index=False)
final_df.to_csv(os.path.join(expert_response_dir, 'cowLR_response_Dan.csv'), index=False)

matrix = winner_loser_df.pivot(index='winner', columns='loser', values='degree').fillna(0)

"""
###############################################################################
###################### merge different experts together #######################
###############################################################################
"""

exp1= pd.read_csv(os.path.join(expert_response_dir, "winner_loser_Dan.csv"))
exp2 = pd.read_csv(os.path.join(expert_response_dir, "winner_loser_Wali.csv"))
exp_all = pd.concat([exp1, exp2], ignore_index=True)
exp_all.to_csv(os.path.join(expert_response_dir, 'winner_loser_merged.csv'), index=False)

"""
###############################################################################
################ Average response from different experts ######################
###############################################################################
"""

exp1_LR= pd.read_csv(os.path.join(expert_response_dir, "cowLR_response_Dan.csv"))
exp2_LR = pd.read_csv(os.path.join(expert_response_dir, "cowLR_response_Wali.csv"))
exp_all_LR = pd.concat([exp1_LR, exp2_LR], ignore_index=True)

# calculate the mean response for each unique set of cow_L and cow_R
mean_responses = exp_all_LR.groupby(['cow_L', 'cow_R'])['response'].mean().reset_index()
winner_loser_avg = create_winner_loser_degree_df(mean_responses)
winner_loser_avg[["expert"]] = "avg_D_W"
winner_loser_avg.to_csv(os.path.join(expert_response_dir, 'winner_loser_avg.csv'), index=False)