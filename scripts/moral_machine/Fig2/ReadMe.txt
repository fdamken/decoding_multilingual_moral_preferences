Documentation for generating plot in Figure 2 and related SI figures.  

0- File RobotoCondensed-Regular.ttf 
font-family of Roboto Condensed used in label generation


1- File MMFunctionsShared.R [Run this file before other files]
++ Input: 
No input

++ Output:
No output


2- File MMAnalysisShared.R
++ Input:
SharedResponses.csv
SharedResponsesSurvey.csv
SharedResponsesFullFirstSessions.csv

++ Output
Fig 2, 
Extended Data Fig 1-3
SI Fig S3-S5
CountriesChangePr.csv
CountriesNoDescriptionChangePr.csv
Other data frames (.rdata)


3- File SharedMMDemoStats.R
++ Input:
SharedResponsesSurvey.csv

++ Output
Extended Data Fig 6


4- File SharedMMFunctionsExtraAnalysis.R [Run this file before the following files]
++ Input: 
No input

++ Output:
No output


5- File SharedMMExtraAnalysis.R
++ Input:
SharedResponsesSurvey.csv

++ Output
Extended Data Table 1 (a screenshot of Demographics.html)


6- File SharedMMPostStratPUMS.R [Run this file before the following file]
++ Input:
SharedResponsesSurvey.csv
ss16pusa.csv
ss16pusb.csv
ss16pusc.csv
ss16pusd.csv

++ Output
Extended Data Fig 7 (e)
USGenderDist.rdata
USIncomeDist.rdata
USEducationDist.rdata
USAgeDist.rdata


7- File SharedUSUserDistribution.R
++ Input:
USGenderDist.rdata
USIncomeDist.rdata
USEducationDist.rdata
USAgeDist.rdata

++ Output
Extended Data Fig 7 (a-d)


8- File SharedPairs.R
++ Input:
CountriesChangePr.csv

++ Output
SI Fig S6

9- File LastMinute.R [contains last minute cosmetic changes to Fig 2 (a), Extended Data Fig1-3, and Extended Data Fig 7(e)]
++ Input:
plotdataSIRobustExternalDescription.rdata
plotdataSIRobustExternalTemplate.rdata
plotdataSIRobustExternalAllDatasets.rdata
plotdataSIRobustInternalScenarioOrder.rdata
plotdataSIRobustInternalProfileOrder.rdata
plotdataSIRobustTheoActu.rdata
plotdataSIpoststratification.rdata
plotdataUserGender.rdata
plotdataUserAge.rdata
plotdataUserPolitical.rdata
plotdataUserReligious.rdata
plotdataUserIncome.rdata
plotdataUserEducation.rdata
plotdatamain.rdata
plotdatautil.rdata

++ Output
Fig 2 (a)
Extended Data Fig1-3
Extended Data Fig 7(e)

