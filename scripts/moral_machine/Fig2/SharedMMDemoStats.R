# The Moral Machine Experiment
# Edmond Awad
# Extended Data Fig 6 (Survey Demographics Stats)
##############

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
demo <- fread(input="SharedResponsesSurvey.csv")
proc.time() - pt


demo.gender <- demo[-which(demo$Review_gender %in% c("","apache helicopter","default")),]
plotdata.gender <- demo.gender %>% group_by(Review_gender) %>% summarise(count = round(length(UserID)/nrow(demo.gender),2))
plotdata.gender$Review_gender <- paste0(toupper(substring(plotdata.gender$Review_gender,1,1)),substring(plotdata.gender$Review_gender,2))
plotdata.gender$Review_gender <- factor(plotdata.gender$Review_gender,levels = plotdata.gender$Review_gender[c(2,1,3)])

pdf(file="MMgender.pdf", width = 8, height = 8)
ggplot(plotdata.gender,aes(x=Review_gender,y=count,fill=Review_gender), color=Review_gender) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  labs(title="Gender distribution of MM respondents")+
  xlab("")+
  ylab("\nProportion")+
  ylim(0,0.75)+
  theme_bw()+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.y = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))

dev.off()

demo.income <- demo[-which(demo$Review_income %in% c("default")),]
demo.income$Review_income <- gsub("over10000","above100000",demo.income$Review_income)
plotdata.income <- demo.income %>% group_by(Review_income) %>% summarise(count = round(length(UserID)/nrow(demo.income),2))

plotdata.income$Review_income <- gsub("above100000","100000",plotdata.income$Review_income)
plotdata.income$Review_income <- gsub("under5000","-1",plotdata.income$Review_income)

plotdata.income <- plotdata.income[c(9,5,1:4,6:8),]

plotdata.income$Review_income[1:8] <- paste0("$",
                                             as.character(format(as.numeric(plotdata.income$Review_income[1:8])+1,big.mark=",", trim=TRUE)),
                                             " - $",as.character(format(as.numeric(plotdata.income$Review_income[2:9]),big.mark=",", trim=TRUE)))
plotdata.income$Review_income[9] <- paste0("More than $",as.character(format(as.numeric(plotdata.income$Review_income[9])+1,big.mark=",", trim=TRUE)))
plotdata.income$Review_income <- factor(plotdata.income$Review_income,levels = rev(plotdata.income$Review_income))


pdf(file="MMincome.pdf", width = 9, height = 9)
ggplot(plotdata.income,aes(x=Review_income,y=count,fill=Review_income), color=Review_income) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  #geom_text(aes(label=round(count,2)),size = 9, position = position_stack(vjust = 0.9),color="black")+
  labs(title="Income distribution of MM respondents")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.5)+
  theme_bw()+
  scale_colour_brewer(palette = "Greens")+
  scale_fill_brewer(palette = "Greens")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="X",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=24,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))

dev.off()

demo.education <- demo[-which(demo$Review_education %in% c("default")),]
plotdata.education <- demo.education %>% group_by(Review_education) %>% summarise(count = round(length(UserID)/nrow(demo.education),2))

plotdata.education$Review_education <- c("Bachelor Degree", "Attended College","Graduate Degree",
                                         "High School Diploma","Others","Attended High School","Vocational Training")

plotdata.education <- plotdata.education[c(5:6,4,7,2,1,3),]
plotdata.education$Review_education <- factor(plotdata.education$Review_education,levels = plotdata.education$Review_education)


pdf(file="MMeducation.pdf", width = 9, height = 9)
ggplot(plotdata.education,aes(x=Review_education,y=count,fill=Review_education), color=Review_education) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  #geom_text(aes(label=round(count,2)),size = 9, position = position_stack(vjust = 0.9),color="black")+
  labs(title="Education distribution of MM respondents")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.25)+
  theme_bw()+
  #scale_color_manual(name="", values=c("#e41a1c","#377EB8"))+
  #scale_fill_manual(name="", values=c("#e41a1c","#377EB8"))+
  scale_colour_brewer(palette = "Oranges")+
  scale_fill_brewer(palette = "Oranges")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="X",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=24,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))

dev.off()

demo.age <- demo[-which(demo$Review_age<1 | demo$Review_age>100 |is.na(demo$Review_age)),]
demo.age <- demo.age[-which(demo.age$Review_gender %in% c("","apache helicopter","default")),]

demo.age$Review_gender <- paste0(toupper(substring(demo.age$Review_gender,1,1)),substring(demo.age$Review_gender,2))
demo.age$Review_gender <- factor(demo.age$Review_gender,levels = rev(c("Male","Female","Others")))

pdf(file="MMage.pdf", width = 12, height = 6)
ggplot(demo.age, aes(Review_age, fill = Review_gender)) + 
  geom_histogram(position = "stack", binwidth=2)+
  labs(title="Age distribution of MM respondents",fill = "Gender")+
  xlab("Age")+
  ylab("\nFrequency")+
  #coord_flip()+
  xlim(0,100)+
  theme_bw()+
  #scale_color_manual(name="", values=c("#e41a1c","#377EB8"))+
  #scale_fill_manual(name="", values=c("#e41a1c","#377EB8"))+
  scale_colour_brewer(palette = "Set1",direction = -1)+
  scale_fill_brewer(palette = "Set1",direction = -1)+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="right",aspect.ratio=1/1.5,plot.title = element_text(size=24,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.y = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),axis.title.x = element_text(size=26),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))

dev.off()
  
