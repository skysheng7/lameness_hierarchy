library(EloRating)
library(EloSteepness)
library(RColorBrewer)
library(dplyr)
source("helpers.R")


# load in the data
# all 55 HITs' response
setwd("C:/Users/skysheng/OneDrive - UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/Sora Jeong/results/Amazon MTurk click worker response")
winner_loser <- read.csv("winner_loser_55HITs.csv", header = TRUE, sep = ",")
cowLR <- read.csv("cowLR_response_clickWorker_55HITS.csv", header = TRUE, sep = ",")

# each of the 55 HITs have the same number of workers
winner_loser_sampled <- read.csv("winner_loser_sampled_55HITs.csv", header = TRUE, sep = ",")
cowLR_sampled <- read.csv("cowLR_response_clickWorker_sampled_55HITS.csv", header = TRUE, sep = ",")

# 55 HITs: delete all responses between the 2 cows if average click worker response is (-1, 1)
winner_loser_sampled_delete <- read.csv("winner_loser_sampled_delete_pairs_55HITs.csv", header = TRUE, sep = ",")

# 55 HITs: if average click worker response is between (-1, 1) create 
# min_worker_num/2 A wins B, min_worker_num/2 B wins A
winner_loser_sampled_exchannge0 <- read.csv("winner_loser_sampled_exchange0_55HITs.csv", header = TRUE, sep = ",")

# 55 HITs: if average click worker response is between (-1, 1) create 
# min_worker_num/2 A wins B, min_worker_num/2 B wins A
winner_loser_sampled_ind_exchannge0 <- read.csv("winner_loser_sampled_ind_exchange0_55HITs.csv", header = TRUE, sep = ",")

# 5 milestone cows: min number of comparisons
winner_loser_milestone_min <- read.csv('winner_loser_milestone_min_55HITs.csv', header = TRUE, sep = ",")

# 5 milestone cows: maximum number of comparisons
winner_loser_milestone_max <- read.csv('winner_loser_milestone_max_55HITs.csv', header = TRUE, sep = ",")

# 12 rounds of expert traditional gait score
setwd("C:/Users/skysheng/OneDrive - UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/results/30_cow_gs_HIT_launch")
gs_record <- read.csv("gs_response_combined_avg_Sep-10-2023.csv", header = TRUE, sep = ",")
gs_record2 <- gs_record[, c("Cow", "GS")]

# load experts' eloSteepness results
setwd("C:/Users/skysheng/OneDrive - UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/results/elo_steepness_rank")
expert_eloSteep <- read.csv("lame_rank_randomized_EloSteep_summary_with_tie.csv", header = TRUE, sep = ",")
expert_eloSteep$X <- NULL

output_dir <- "C:/Users/skysheng/OneDrive - UBC/University of British Columbia/Research/PhD Project/Amazon project phase 2/results/elo_steepness_rank/"


################################################################################
################ how many responses (worker) per unique pair ###################
################################################################################
# all 54 HITs
count_worker_per_HIT <- count_unique_worker_per_HIT(cowLR)
count_worker_per_pair <- count_unique_worker_per_pair(cowLR)

# sample the same number of workers per video pair
count_worker_per_pair_sampled <- count_unique_worker_per_pair(cowLR_sampled)
min_worker_num <- min(count_worker_per_pair_sampled$worker_num)
################################################################################
############# handle tie by duplicate row and flip winner loser#################
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed <- swap_winner_loser(winner_loser, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed, expert_eloSteep, output_dir, "eloSteep_with_tie", "click_worker", gs_record2)

################################################################################
################# sample same number of worker per pair ########################
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_sampled <- swap_winner_loser(winner_loser_sampled, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_sampled, click_worker_experts, output_dir, "eloSteep_with_tie_sampled", "click_worker", gs_record2)

################################################################################
### delete all responses between the 2 cows if average click worker response####
############################ is between (-1, 1) ################################
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_sampled_delete <- swap_winner_loser(winner_loser_sampled_delete, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_sampled_delete, click_worker_experts, output_dir, "eloSteep_with_tie_sampled_delete", "click_worker", gs_record2)

################################################################################
########## if average click worker response is between (-1, 1) create ##########
############ min_worker_num/2 A wins B, min_worker_num/2 B wins A ##############
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_sampled_exchange0 <- swap_winner_loser(winner_loser_sampled_exchannge0, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_sampled_exchange0, click_worker_experts, output_dir, "eloSteep_with_tie_sampled_exchange0", "click_worker", gs_record2)

################################################################################
########## if individual click worker response is between (-1, 1) ##############
######################### set his/her response to 0 ############################
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_sampled_ind_exchange0 <- swap_winner_loser(winner_loser_sampled_ind_exchannge0, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_sampled_ind_exchange0, click_worker_experts, output_dir, "eloSteep_with_tie_sampled_ind_exchange0", "click_worker", gs_record2)

################################################################################
############################ pick 5 milestone cows #############################
## 7045 (GS 1.9), 6096 (GS 2.4), 6086(GS 2.87), 4035 (GS 3.1), 5087 (GS 3.9) ###
## use minimum number of comparisons: start comparing with the most healthy ####
## cow, stop when the current cow is more than 1 degree more healthy than the ##
################################# milestone cows ###############################
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_milestone_min <- swap_winner_loser(winner_loser_milestone_min, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_milestone_min, click_worker_experts, output_dir, "eloSteep_with_tie_sampled_milestone_min", "click_worker", gs_record2)

################################################################################
############################ pick 5 milestone cows #############################
## 7045 (GS 1.9), 6096 (GS 2.4), 6086(GS 2.87), 4035 (GS 3.1), 5087 (GS 3.9) ###
## use maximum number of comparisons: compare with each of the 5 milestone cows#
################################################################################
# handle ties: duplicate the rows where degree = 0, 1 row: A wins over B, 2nd row: B wins over A
winn_loser_processed_milestone_max <- swap_winner_loser(winner_loser_milestone_max, FALSE)
click_worker_experts <- random_elo_steep(winn_loser_processed_milestone_max, click_worker_experts, output_dir, "eloSteep_with_tie_sampled_milestone_max", "click_worker", gs_record2)