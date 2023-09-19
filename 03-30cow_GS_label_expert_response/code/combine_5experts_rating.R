library(lubridate)
library(irr)
gs_p1 <- read.csv("../results/gs_response_Aug-12-2023.csv", header = TRUE)
gs_p2 <- read.csv("../results/gs_response_Wali_Jul-10-2023.csv", header = TRUE)
gs_p3 <- read.csv("../results/gs_response_Wali_Jul-14-2023.csv", header = TRUE)
gs_p4 <- read.csv("../results/gs_response_Wali_Jul-18-2023.csv", header = TRUE)
gs_p5 <- read.csv("../results/gs_response_Sep-10-2023.csv", header = TRUE)

gs <- rbind(gs_p1, gs_p2)
gs <- rbind(gs, gs_p3)
gs <- rbind(gs, gs_p4)
gs <- rbind(gs, gs_p5)

# remove worker "SB" as she used a different lameness assessment method than the other workers
gs <- gs[which(gs$Worker_id != "SB"),]

######################## GS average processing #################################
# take the avearge across all experts for each cow
gs_avg <- aggregate(gs$GS, by = list(gs$Cow), FUN = mean)
colnames(gs_avg) <- c("Cow", "GS")

###################### intraobserver reliability ###############################
# you can only calculate intraobserver reliability if the expert answered >=2 times
temp <- gs[which(gs$Cow == 4008),]
expert_retain <- unique(temp$Worker_id[duplicated(temp$Worker_id)])
gs_retain <- gs[which(gs$Worker_id %in% expert_retain),]
gs_retain <- gs_retain[, c("Cow", "Worker_id", "GS_round", "GS")]

# calculate intraobserver reliability using iCC
# Get the unique worker IDs
workers <- unique(gs_retain$Worker_id)

# Initialize an empty vector to store the ICC for each worker
icc_values <- numeric(length(workers))

# Loop over each unique worker
for (i in seq_along(workers)) {
  # Subset the data for the current worker
  worker_data <- gs_retain[gs_retain$Worker_id == workers[i], ]
  
  # Reshape the data to wide format, with one row per cow and one column per observation
  worker_data_wide <- reshape(worker_data, idvar = c("Worker_id", "Cow"), timevar = "GS_round", direction = "wide")
  
  # Calculate the ICC for the current worker
  icc_result <- icc(worker_data_wide[, 3:ncol(worker_data_wide)],model = "twoway", type = "agreement", unit = "single")
  
  # Store the ICC value
  icc_values[i] <- icc_result$value
}

# Combine the worker IDs and ICC values into a data frame
icc_df <- data.frame(Worker_id = workers, ICC = icc_values)
icc_mean <- mean(icc_df$ICC)
icc_sd <- sd(icc_df$ICC)

###################### interobserver reliability ###############################
gs_retain2 <- gs[which(gs$GS_round == 1),]
gs_retain2 <- gs_retain2[, c("Cow", "Worker_id", "GS")]

# change data orientation
worker_data_wide_inter <- reshape(gs_retain2, idvar = c("Cow"), timevar = "Worker_id", direction = "wide")
# Calculate the ICC for the current worker
icc_result_inter <- icc(worker_data_wide_inter[, 2:ncol(worker_data_wide_inter)],model = "twoway", type = "agreement", unit = "single")
icc_values_inter <- icc_result_inter$value  # 0.47

write.csv(gs, file = "../results/gs_response_combined.csv")
write.csv(gs_avg, file = "../results/gs_response_combined_avg.csv")
write.csv(icc_df, file = "../results/intraobserver_reliability.csv")