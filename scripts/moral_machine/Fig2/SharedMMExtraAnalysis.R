# The Moral Machine Experiment
# Edmond Awad
# Extra Analysis - Extended Data Table 1
##############

# First, run MMFunctionsShared.R
# Then, run SharedMMFunctionsExtraAnalysis.R

# Set up
library(ggplot2)
library(reshape2)
library(dplyr)
library(tidyr)
library(AER)
library(sandwich)
library(multiwayvcov)
library(data.table)
library(lme4)
library(stargazer)
library(lfe)



pt = proc.time()
profiles.S <- fread(input="SharedResponsesSurvey.csv")
proc.time() - pt


# Preprocess variables
profiles.S <- PreprocessProfiles(profiles.S)
profiles.S <- AddUserColumns(profiles.S)
profiles.S <- RecodeColumns(profiles.S)
profiles.S <- PrepareDemColumns(profiles.S)

# Regress
contVars <- c("Review_age.z","Review_ContinuousIncome.z","Review_political.z","Review_religious.z")

lev <- levels(profiles.S$ScenarioType)
if (levels(profiles.S$ScenarioType)[1]=="") lev <- levels(profiles.S$ScenarioType)[2:8]
lev <- lev[c(3,2,5,1,7,6)]

# Remove redundant users
b <- profiles.S %>% group_by(UserID,ExtendedSessionID) %>% summarise(count = length(PreferredIsChosen))
d <- b[!duplicated(b$UserID),"ExtendedSessionID"]
profiles.S.C <- profiles.S[which(profiles.S$ExtendedSessionID %in% d$ExtendedSessionID),]

# Run regressions
## Intervention
Temp <- profiles.S.C
lm.Temp.I <- felm(StayIsChosen ~ as.factor(CrossingSignal)+as.factor(Barrier)+
                      Review_gender+Review_age.z+Review_ContinuousIncome.z+Review_CollegeEducated+
                      Review_political.z+Review_religious.z|0|0|UserID,
                    data=Temp)

## Relation to AV
Temp <- profiles.S.C[which(profiles.S.C$CrossingSignal==0 & profiles.S.C$PedPed==0),]
lm.Temp.B <- felm(PedestriansIsChosen ~ as.factor(Intervention)+
                      Review_gender+Review_age.z+Review_ContinuousIncome.z+Review_CollegeEducated+
                      Review_political.z+Review_religious.z|0|0|UserID,
                   data=Temp)

## Legality
Temp <- profiles.S.C[which(profiles.S.C$CrossingSignal!=0 & profiles.S.C$PedPed==1),]
lm.Temp.C <- felm(LegalIsChosen ~ as.factor(Intervention)+
                      Review_gender+Review_age.z+Review_ContinuousIncome.z+Review_CollegeEducated+
                      Review_political.z+Review_religious.z|0|0|UserID,
                    data=Temp)

## character attributes
lm.Temp <- list()
for(i in 1:6){
  Temp <- profiles.S.C[which(profiles.S.C$ScenarioType==lev[i]),]
  lm.Temp[[i]] <- felm(PreferredIsChosen ~ as.factor(Intervention)+as.factor(CrossingSignal)+as.factor(Barrier)+
                           Review_gender+Review_age.z+Review_ContinuousIncome.z+Review_CollegeEducated+
                           Review_political.z+Review_religious.z|0|0|UserID,
                        data=Temp)
}



stargazer(lm.Temp.I,lm.Temp.B,lm.Temp.C,lm.Temp, 
          align=TRUE, type="html", out="Demographics.html", font.size = "footnotesize", star.cutoffs = c(0.01, 0.001, 0.0001),
          title="Demographics", object.names = FALSE, 
          column.labels = c("Preference<br> for Inaction","Sparing<br> Pedestrians","Sparing the<br> Lawful",
                            "Sparing<br> Females","Sparing the<br> Fit", "Sparing<br> Higher Status",
                            "Sparing the<br> Young","Sparing More<br> Characters","Sparing<br> Humans"), 
          dep.var.caption ="" , #column.separate = c(3, 3),
          dep.var.labels.include = FALSE, 
          omit = "as.factor",
          order= c("Review_gendermale","Review_age.z","Review_ContinuousIncome.z","Review_CollegeEducated",
                   "Review_political.z", "Review_religious.z"),
          covariate.labels = c("Male","Age","Income","Is college educated",
                               "Political views (conservative to progressive)", "Religiousity",
                               "Constant"),
          add.lines = list(#c("Subject Random Effects?", rep("Yes",9)),
                           c("Structural Covariates",rep("Yes",9))),
          omit.stat = c("ser", "f","aic","bic","ll","rsq","adj.rsq"),#keep.stat = c("n"),
          notes = "***,**,* significant at 0.01%, 0.1% and 1% levels, respectively.",
          notes.label = "", notes.append = FALSE, notes.align = "l")

