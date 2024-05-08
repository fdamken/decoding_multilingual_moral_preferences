# The Moral Machine Experiment
# Edmond Awad
# Fig 2, Extended Data Fig 1-3, and SI Fig S3-S5
# Output files: Country-level data, used as input for Fig.3-4, Extended Data Fig 4-5, ED Table 2 and SI Fig S6-S11
##############

setwd("/home/fdamken/Development/study/tinypaper/scripts/moral_machine/Fig2")

# First, run all of MMFunctionsShared.R
source(file = "MMFunctionsShared.R")
# Then,  follow below.

# Set up
library(ggplot2)
library(reshape2)
library(dplyr)
library(tidyr)
library(AER)
library(sandwich)
library(multiwayvcov)
library(data.table)


# Loading data as a data.table
pt = proc.time()
profiles <- fread(input = "SharedResponses.csv")
proc.time() - pt

pt = proc.time()
proc.time() - pt

profiles <- PreprocessProfiles(profiles)


# # Main Figure 2 - (a)
# Coeffs.main <- GetMainEffectSizes(profiles, T, 9)
# plotdata.main <- GetPlotData(Coeffs.main, T, 9)
#
# Coeffs.util <- GetMainEffectSizes.Util(profiles)
# plotdata.util <- GetPlotData.Util(Coeffs.util)
#
# ## Save them
# save(plotdata.main, file = "plotdatamain.rdata")
# save(plotdata.util, file = "plotdatautil.rdata")
# ## Plot them
# PlotAndSave(plotdata.main, T, "MainChangePr", plotdata.util)
#
#
# # Main Figure 2 - (b)
# filename <- "Characters"
# Coeffs.characters <- GetMainEffectSizes.Characters(profiles, "Random", 1)
# plotdata.characters.all <- GetPlotData.Characters(Coeffs.characters, "Random", 1)
# # Save it
# save(plotdata.characters.all, file = "plotdatacharacters.rdata")
# # Plot it
# PlotAndSave.Characters(plotdata.characters.all, "Random", T, filename)
#
#
# # Extended Data Figures
# ## Extended Data Fig 1
# ## ED Fig 1 (a)
# # Robustness checks - Internal validity
# filename <- "RobustnessInternal"
# ## Scenario Order
# r <- 9
# vals <- c(1:13)
# Coeffs <- GetEffectSizes.Inter.Others(profiles, r, profiles$ScenarioOrder, vals)
# plotdata <- GetPlotData.Inter.Others(Coeffs, vals, F, F)
# AttrLabel <- "Scenario Order"
# plotdata$Label <- factor(plotdata$Label, levels = rev(levels(plotdata$Label)))
# plotdata$Attribute <- rep(factor(c(1:13), levels = c(13:1)), each = r)
# # Save it
# save(plotdata, file = "plotdataSIRobustInternalScenarioOrder.rdata")
# # Plot it
# PlotAndSave.Split.Order(plotdata, AttrLabel, F, filename)
#
# ## ED Fig 1 (b)
# ## Profile Order
# AttrLabel <- "Profile is on left"
# r <- 9
# vals <- c(0:1)
# Coeffs <- GetEffectSizes.Inter.Others(profiles, r, profiles$LeftHand, vals)
# plotdata <- GetPlotData.Inter.Others(Coeffs, vals, F, F)
# # Save it
# save(plotdata, file = "plotdataSIRobustInternalProfileOrder.rdata")
# # Plot it
# PlotAndSave.Split(plotdata, AttrLabel, F, filename)
#
#
# ## ED Fig 1 (c)
# ## Theoretical vs. actual distribution of conditions
# filename <- "RobustnessInternal"
# r <- 9
#
# ### main effects using theoretical distribution
# load("plotdatamain.rdata")
#
# ### main effects using actual distribution
# #Coeffs.main.AW <- GetMainEffectSizesActualWeights(profiles[sample(c(1:70000000),100000),],F,9)
#
# Coeffs.main.AW <- GetMainEffectSizesActualWeights(profiles, F, 9)
# plotdata.main.AW <- GetPlotData(Coeffs.main.AW, T, 9)
#
# ### Combine all
# plotdata.main.TheoActu <- rbind(cbind(plotdata.main, Attribute = "Theortical Distribution"),
#                                 cbind(plotdata.main.AW, Attribute = "Actual Distribution"))
#
# # Save it
# save(plotdata.main.TheoActu, file = "plotdataSIRobustTheoActu.rdata")
# # Plot it
# PlotAndSave.Split(plotdata.main.TheoActu, "Actual", F, filename)
#
# ## ED Fig 2 (c)
# ## Dataset used
# ### all data
# load("plotdatamain.rdata")
#
#
# # Supplemential Information Figures
# ## Fig S3 (same as Fig 2 (a) w/ confidence intervals)
# Coeffs.main.SI <- GetMainEffectSizes(profiles, F, 9)
# plotdata.main.SI <- GetPlotData(Coeffs.main.SI, F, 9)
# PlotAndSave(plotdata.main.SI, F, "MainChangePr", plotdata.util)
#
# ## Fig S4
# ## Fig S4 (a)
# ##Inter Attr
# filename <- "Inter"
# ## Interventionism
# Attr = "Intervention"
# r <- 7
# if (Attr == "Intervention") r <- 8
# Coeffs <- GetEffectSizes.Inter.Att(profiles, r, Attr)
# plotdata <- GetPlotData.Inter.Attr(Coeffs, F, r, Attr)
# # Save it
# save(plotdata, file = "plotdataSIInterIntervention.rdata")
# # Plot it
# PlotAndSave.Split(plotdata, Attr, F, filename)
#
# ## Fig S4 (b)
# ## Relation to AV
# Attr = "Barrier"
# r <- 7
# if (Attr == "Intervention") r <- 8
# Coeffs <- GetEffectSizes.Inter.Att(profiles, r, Attr)
# plotdata <- GetPlotData.Inter.Attr(Coeffs, F, r, Attr)
# # Save it
# save(plotdata, file = "plotdataSIInterRelation.rdata")
# # Plot it
# PlotAndSave.Split(plotdata, Attr, F, filename)
#
# ## Fig S4 (c)
# ## Legality
# Attr = "CrossingSignal"
# r <- 7
# if (Attr == "Intervention") r <- 8
# Coeffs <- GetEffectSizes.Inter.Att(profiles, r, Attr)
# plotdata <- GetPlotData.Inter.Attr(Coeffs, F, r, Attr)
# # Save it
# save(plotdata, file = "plotdataSIInterLegality.rdata")
# # Plot it
# PlotAndSave.Split(plotdata, Attr, F, filename)
#
#
# ## Fig S5 (a-f)
# #SI Figure Characters effect within dimensions
# filename <- "Characters"
# k = 1
# r <- 9
# for (scope in names(characters.all)[-6]) {
#   Coeffs.characters <- GetMainEffectSizes.Characters(profiles, scope, k)
#   plotdata.characters <- GetPlotData.Characters(Coeffs.characters, scope, k)
#   # Save them
#   save(plotdata.characters, file = paste0("plotdataSICharacters", scope, ".rdata"))
#   # Plot them
#   PlotAndSave.Characters(plotdata.characters, scope, F, filename)
# }


######################
# Get stratified effect sizes for locations (used elsewhere for cross-country figures)
r = 9
###########
# 1. Countries
# Use the first function to tinker with the threshold
# For example, using 2500 records per country as a threshold will result with k countries. Is that enough?
vals <- GetFilteredList(profiles, "UserCountry3", 100)
k = length(vals)

# Use the second function to calculate the effect sizes for each country. This returns a matrix
Coeffs <- GetEffectSizes.Inter.Others(profiles, r, profiles$UserCountry3, vals)

# Use the third function to prepare the final data frame that you want to save
finaldata <- GetFinalDF(Coeffs, vals)

# Save to a csv
pt = proc.time()
fwrite(file = "CountriesChangePr.csv", x = finaldata, row.names = T)
proc.time() - pt
