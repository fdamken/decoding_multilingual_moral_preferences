# The Moral Machine Experiment
# Edmond Awad
# Extra Analysis Functions
##############

# Set up
library(tidyverse)
library(reshape2)
library(AER)
library(sandwich)
library(multiwayvcov)
library(data.table)
library(hrbrthemes)
library(extrafont)
# font_import()
# y
fonts()
#loadfonts()
library(ggthemes)




# New functions -- Revise and resubmit
PreferredLevel <- list(Age = "Young",
                       Fitness = "Fit",
                       `Social Status` = "High",
                       Species = "Hoomans",
                       Gender = "Female",
                       Utilitarian = "More",
                       Random = "Rand")

NonPreferredLevel <- list(Age = "Old",
                          Fitness = "Fat",
                          `Social Status` = "Low",
                          Species = "Pets",
                          Gender = "Male",
                          Utilitarian = "Less",
                          Random = "Rand")

PreferredLevelF <- function(sType){
  return(as.character(unlist(PreferredLevel[sType])))
}

RecodeColumns <- function(profiles){
  profiles[,PreferredCol:= PreferredLevelF(as.character(ScenarioType))]
  profiles[,PreferredIsChosen:= ifelse(!xor(AttributeLevel==PreferredCol,Saved),TRUE,FALSE)]
  profiles[,StayIsChosen:= ifelse(!xor(Intervention==0,Saved),TRUE,FALSE)]
  profiles[,PedestriansIsChosen:= ifelse(!xor(Barrier==0,Saved),TRUE,FALSE)]
  profiles[,LegalIsChosen:= ifelse(!xor(CrossingSignal==1,Saved),TRUE,FALSE)]
  return(profiles)
}

# Prepare demographic columns
PrepareDemColumns <- function(profiles){
  profiles[,Review_gender:=gsub("default",NA,Review_gender)]
  profiles[,Review_gender:=gsub("others",NA,Review_gender)]
  profiles[,Review_gender:= factor(Review_gender,levels=c("female","male"))]
  
  profiles[,Review_income:=gsub("default",NA,Review_income)]
  profiles[,Review_income:=gsub("over10000","above100000",Review_income)]
  profiles[,Review_income:= factor(Review_income,levels=c("under5000","5000","10000","15000","25000",
                                                          "35000","50000","80000","above100000"))]
  profiles[,Review_ContinuousIncome:= case_when(Review_income == "under5000"~ 2500,
                                                Review_income == "5000"~7500,
                                                Review_income == "10000"~12500,
                                                Review_income == "15000"~20000,
                                                Review_income == "25000"~30000,
                                                Review_income == "35000"~42500,
                                                Review_income == "50000"~65000,
                                                Review_income == "80000"~90000,
                                                Review_income == "above100000"~150000)]
  profiles[,Review_ContinuousIncome.z:=as.numeric(scale(Review_ContinuousIncome))]
  
  profiles[,Review_education:=gsub("default",NA,Review_education)]
  profiles[,Review_education:= factor(Review_education,levels=c("underHigh","high","vocational","college",
                                                                "bachelor","graduate","others"))]
  profiles[,Review_CollegeEducated:= ifelse(Review_education=="others",NA,
                                            ifelse(Review_education %in% c("college","bachelor","graduate"),1,0))]
  
  
  profiles[,Review_age:=ifelse(Review_age>15 & Review_age<75,Review_age,NA)]
  profiles[,Review_age.z:=as.numeric(scale(Review_age))]
  
  profiles[,Review_political.z:=as.numeric(scale(Review_political))]
  
  profiles[,Review_religious.z:=as.numeric(scale(Review_religious))]
  
  return(profiles)
}

