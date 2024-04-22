# The Moral Machine Experiment
# Edmond Awad
# Extra Analysis (Post-stratification) - Extended Data Fig 7 (e)
##############

# First, run MMFunctionsShared.R
# Then, run SharedMMFunctionsExtraAnalysis.R
# Then, follow below

#Set up
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
library(readxl)
library(data.table)



pt = proc.time()
profiles.S <- fread(input="SharedResponsesSurvey.csv")
proc.time() - pt


# Preprocess variables
profiles.S <- PreprocessProfiles(profiles.S)
profiles.S <- AddUserColumns(profiles.S)
profiles.S <- RecodeColumns(profiles.S)
profiles.S <- PrepareDemColumns(profiles.S)

# Read US PUMS data
pt = proc.time()
pums.a <- fread(input="ss16pusa.csv")
pums.b <- fread(input="ss16pusb.csv")
pums.c <- fread(input="ss16pusc.csv")
pums.d <- fread(input="ss16pusd.csv")
proc.time() - pt

pums <- rbind(pums.a,pums.b,pums.c,pums.d)


# Plan
## Filter out Puerto Rico
pums <- pums[which(ST!=72),]

## filter age
pums <- pums[which(AGEP>15 & AGEP<75),]

## Correct income for years
pums[,CorrPINCP:=as.numeric(PINCP)*as.numeric(ADJINC)/1000000]
  
## Create categorical columns
pums[,Gender:= case_when(SEX==1 ~"male",
                         SEX==2 ~"female")]
                                
pums[,IncomeBracket:= case_when(CorrPINCP<5000 ~"under5000",
                                CorrPINCP>=5000 & CorrPINCP<10000 ~"5000",
                                CorrPINCP>=10000 & CorrPINCP<15000 ~"10000",
                                CorrPINCP>=15000 & CorrPINCP<25000 ~"15000",
                                CorrPINCP>=25000 & CorrPINCP<35000 ~"25000",
                                CorrPINCP>=35000 & CorrPINCP<50000 ~"35000",
                                CorrPINCP>=50000 & CorrPINCP<80000 ~"50000",
                                CorrPINCP>=80000 & CorrPINCP<100000 ~"80000",
                                CorrPINCP>=100000 ~"above100000")]
pums[,IncomeBracketSmall:= case_when(CorrPINCP<5000 ~"under5000",
                                CorrPINCP>=5000 & CorrPINCP<25000 ~"5000",
                                CorrPINCP>=25000 & CorrPINCP<50000 ~"25000",
                                CorrPINCP>=50000 & CorrPINCP<100000 ~"50000",
                                CorrPINCP>=100000 ~"above100000")]

pums[,AgeBracket:= case_when(AGEP>=15 & AGEP<25 ~"15-24",
                             AGEP>=25 & AGEP<35 ~"25-34",
                             AGEP>=35 & AGEP<45 ~"35-44",
                             AGEP>=45 & AGEP<55 ~"45-54",
                             AGEP>=55 & AGEP<65 ~"55-64",
                             AGEP>=65 & AGEP<75 ~"65-74")]

pums <- pums[-which(SCHL %in% c(17,20)),]

pums[,EducationBracket:= case_when(SCHL<=15 ~"underHigh",
                                   SCHL==16 ~"high",
                                   SCHL %in% c(18:19) ~"college",
                                   SCHL==21 ~"bachelor",
                                   SCHL %in% c(22:24) ~"graduate")]
                                   
## Re-order levels
pums[,Gender:= factor(Gender,levels=c("female","male"))]
pums[,IncomeBracket:= factor(IncomeBracket,levels=c("under5000","5000","10000","15000","25000",
                                                        "35000","50000","80000","above100000"))]
pums[,IncomeBracketSmall:= factor(IncomeBracketSmall,levels=c("under5000","5000","25000",
                                                    "50000","above100000"))]
pums[,EducationBracket:= factor(EducationBracket,levels=c("underHigh","high","college",
                                                              "bachelor","graduate"))]

## group by / correct for weight if needed: sum(PWGTP)
## calculate percentages
pumsPOP <- pums %>% 
  group_by(Gender,AgeBracket,IncomeBracketSmall,EducationBracket) %>% 
  summarise(n = sum(PWGTP)) 
pumsPOP$ACSfreq <- pumsPOP$n/sum(pumsPOP$n)


# Now to the MM data
profiles.S[,Review_ageBracket:= case_when(Review_age>=15 & Review_age<25 ~"15-24",
                                          Review_age>=25 & Review_age<35 ~"25-34",
                                          Review_age>=35 & Review_age<45 ~"35-44",
                                          Review_age>=45 & Review_age<55 ~"45-54",
                                          Review_age>=55 & Review_age<65 ~"55-64",
                                          Review_age>=65 & Review_age<75 ~"65-74")]


profiles.subs <- profiles.S[which(profiles.S$UserCountry3=="USA"),]
profiles.subs[,Review_education:= gsub("vocational",NA,Review_education)]
profiles.subs[,Review_education:= gsub("others",NA,Review_education)]

profiles.subs[,Review_education:= factor(Review_education,levels=c("underHigh","high","college",
                                                          "bachelor","graduate"))]

profiles.subs[,IncomeBracketSmall:= case_when(Review_income=="under5000" ~"under5000",
                                              Review_income %in% c("5000","10000","15000") ~"5000",
                                              Review_income %in% c("25000","35000") ~"25000",
                                              Review_income %in% c("50000","80000") ~"50000",
                                              Review_income=="above100000" ~"above100000")]
profiles.subs[,IncomeBracketSmall:= factor(IncomeBracketSmall,levels=c("under5000","5000","25000",
                                                              "50000","above100000"))]
MMDem <- profiles.subs[,c("UserID","Review_gender","IncomeBracketSmall","Review_education","Review_ageBracket")]


MMDem <- MMDem[which(complete.cases(MMDem)),]
MMDemUU <- MMDem[!duplicated(MMDem$UserID),]

MMDemUUPOP <- MMDemUU %>% 
  group_by(Review_gender,Review_ageBracket,IncomeBracketSmall,Review_education) %>% 
  summarise(n = length(UserID)) 
MMDemUUPOP$MMfreq <- MMDemUUPOP$n/sum(MMDemUUPOP$n)

# Combine both
FreqMerged <-  merge(MMDemUUPOP,pumsPOP,by.x=names(MMDemUUPOP)[1:4],by.y=names(pumsPOP)[1:4])
FreqMerged$ACSfreq <- FreqMerged$n.y/sum(FreqMerged$n.y)

FreqMerged$PostStratWeights <- FreqMerged$ACSfreq/FreqMerged$MMfreq

profiles.subs <- merge(profiles.subs,FreqMerged,by=names(MMDemUUPOP)[1:4],all.x = T)


# Save data for descriptive plots
US.Gender.dist.pums <- pums %>% group_by(Gender) %>% summarize(pumsPOP = sum(PWGTP))
US.Gender.dist.pums$pumsPerc <- US.Gender.dist.pums$pumsPOP/sum(US.Gender.dist.pums$pumsPOP)
US.Gender.dist.MM <- MMDem %>% group_by(Review_gender) %>% summarize(MMPOP = length(UserID))
US.Gender.dist.MM$MMPerc <- US.Gender.dist.MM$MMPOP/sum(US.Gender.dist.MM$MMPOP)
US.Gender.dist <- merge(US.Gender.dist.pums,US.Gender.dist.MM,by.x="Gender",by.y="Review_gender")[,c(1,3,5)]
save(US.Gender.dist, file = "USGenderDist.rdata")

US.Income.dist.pums <- pums %>% group_by(IncomeBracketSmall) %>% summarize(pumsPOP = sum(PWGTP))
US.Income.dist.pums$pumsPerc <- US.Income.dist.pums$pumsPOP/sum(US.Income.dist.pums$pumsPOP)
US.Income.dist.MM <- MMDem %>% group_by(IncomeBracketSmall) %>% summarize(MMPOP = length(UserID))
US.Income.dist.MM$MMPerc <- US.Income.dist.MM$MMPOP/sum(US.Income.dist.MM$MMPOP)
US.Income.dist <- merge(US.Income.dist.pums,US.Income.dist.MM,by.x="IncomeBracketSmall",by.y="IncomeBracketSmall")[,c(1,3,5)]
save(US.Income.dist, file = "USIncomeDist.rdata")

US.Education.dist.pums <- pums %>% group_by(EducationBracket) %>% summarize(pumsPOP = sum(PWGTP))
US.Education.dist.pums$pumsPerc <- US.Education.dist.pums$pumsPOP/sum(US.Education.dist.pums$pumsPOP)
US.Education.dist.MM <- MMDem %>% group_by(Review_education) %>% summarize(MMPOP = length(UserID))
US.Education.dist.MM$MMPerc <- US.Education.dist.MM$MMPOP/sum(US.Education.dist.MM$MMPOP)
US.Education.dist <- merge(US.Education.dist.pums,US.Education.dist.MM,by.x="EducationBracket",by.y="Review_education")[,c(1,3,5)]
save(US.Education.dist, file = "USEducationDist.rdata")

US.Age.dist.pums <- pums %>% group_by(AgeBracket) %>% summarize(pumsPOP = sum(PWGTP))
US.Age.dist.pums$pumsPerc <- US.Age.dist.pums$pumsPOP/sum(US.Age.dist.pums$pumsPOP)
US.Age.dist.MM <- MMDem %>% group_by(Review_ageBracket) %>% summarize(MMPOP = length(UserID))
US.Age.dist.MM$MMPerc <- US.Age.dist.MM$MMPOP/sum(US.Age.dist.MM$MMPOP)
US.Age.dist <- merge(US.Age.dist.pums,US.Age.dist.MM,by.x="AgeBracket",by.y="Review_ageBracket")[,c(1,3,5)]
save(US.Age.dist, file = "USAgeDist.rdata")

# Function for weights
GetWeightedMainEffectSizes <- function(profiles,weightCol,savedata,r){
  Coeffs <- matrix(NA,r,2)
  AttLevels <- levels(profiles$AttributeLevel)
  lev <- levels(profiles$ScenarioType)
  if (levels(profiles$ScenarioType)[1]=="") lev <- levels(profiles$ScenarioType)[2:8]
  lev <- lev[c(3,2,5,1,7,6)]
  
  # For intervention
  profiles$BC.weights <- calcWeightsTheoretical(profiles)*profiles[[weightCol]]
  lm.Int <- lm(Saved ~as.factor(Intervention), data=profiles, weights = BC.weights)
  lm.Int.se <- coeftest(lm.Int, cluster.vcov(lm.Int, cluster = profiles$UserID))[,2]
  Coeffs[1,1] <- lm.Int$coefficients[[2]]
  Coeffs[1,2] <- lm.Int.se[[2]]
  
  # For relationship to vehicle 
  ## Consider only 'no legality' (CrossingSignal==0) and 'passengers vs. pedestrians' (PedPed==0)
  profile.Relation <- profiles[which(profiles$CrossingSignal==0 & profiles$PedPed==0),]
  profile.Relation$BC.weights <- calcWeightsTheoretical(profile.Relation)*profile.Relation[[weightCol]]
  lm.Rel <- lm(Saved ~as.factor(Barrier), data=profile.Relation, weights = BC.weights)
  lm.Rel.se <- coeftest(lm.Rel, cluster.vcov(lm.Rel, cluster = profile.Relation$UserID))[,2]
  Coeffs[2,1] <- lm.Rel$coefficients[[2]]
  Coeffs[2,2] <- lm.Rel.se[[2]]
  
  # Legality 
  ## Exclude 'no legality' (CrossingSignal!=0) and consider only 'pedestrians vs. pedestrians' (PedPed==1)
  profile.Legality <- profiles[which(profiles$CrossingSignal!=0 & profiles$PedPed==1),]
  profile.Legality$CrossingSignal <- factor(profile.Legality$CrossingSignal, levels=levels(profiles$CrossingSignal)[2:3])
  profile.Legality$BC.weights <- calcWeightsTheoretical(profile.Legality)*profile.Legality[[weightCol]]
  lm.Leg <- lm(Saved ~as.factor(CrossingSignal), data=profile.Legality, weights = BC.weights)
  lm.Leg.se <- coeftest(lm.Leg, cluster.vcov(lm.Leg, cluster = profile.Legality$UserID))[,2]
  Coeffs[3,1] <- lm.Leg$coefficients[[2]]
  Coeffs[3,2] <- lm.Leg.se[[2]]
  
  # Six factors (gender, fitness, Social Status, age, utilitarianism, age, and species)
  ## Extract data subsets and run regression for each
  for(i in 1:6){
    Temp <- profiles[which(profiles$ScenarioType==lev[i] & profiles$ScenarioTypeStrict==lev[i]),]
    Temp$AttributeLevel <- factor(Temp$AttributeLevel, levels=AttLevels[(i*2):(i*2+1)])
    Temp$BC.weights <- calcWeightsTheoretical(Temp)*Temp[[weightCol]]    
    lm.Temp <- lm(Saved ~ as.factor(AttributeLevel), data=Temp, weights = BC.weights)
    lm.Temp.se <- coeftest(lm.Temp, cluster.vcov(lm.Temp, cluster = Temp$UserID))[,2]
    Coeffs[i+3,1] <- lm.Temp$coefficients[[2]]
    Coeffs[i+3,2] <- lm.Temp.se[[2]]
    
    # Save to a data frame
    if(savedata){
      var.name <- paste("profile",gsub(" ","",lev[i]),sep=".")
      assign(var.name,Temp)
    }
  }
  return(Coeffs)
}


# Calculate for both
filename <- "ExtraRR"

### Pre
Coeffs.main.pre <- GetMainEffectSizes(profiles.subs,F,9)
plotdata.main.pre <- GetPlotData(Coeffs.main.pre,T,9)

### Post
Coeffs.main.post <- GetWeightedMainEffectSizes(profiles.subs,"PostStratWeights",F,9)
plotdata.main.post <- GetPlotData(Coeffs.main.post,T,9)


### Combine all
plotdata.main.strat <- rbind(cbind(plotdata.main.pre,Attribute="Pre-stratisification"),
                                      cbind(plotdata.main.post,Attribute="Post-stratisification"))
# Save it
save(plotdata.main.strat, file = "plotdataSIpoststratification.rdata")
# Plot it
PlotAndSave.Split(plotdata.main.strat,"Stratification",F,filename)

