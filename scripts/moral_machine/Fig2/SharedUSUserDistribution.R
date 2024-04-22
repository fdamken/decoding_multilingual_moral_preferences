# The Moral Machine Experiment
# Edmond Awad
# Extra Analysis (US User Demographic Distribution) - Extended Data Fig 7 (a-d)
##############

# First, run MMFunctionsShared.R
# Then, run SharedMMFunctionsExtraAnalysis.R
# Then, run SharedMMPostStratPUMS.R to produce .rdata files below
# Then, follow below

# set up
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



load("USGenderDist.rdata")
load("USIncomeDist.rdata")
load("USEducationDist.rdata")
load("USAgeDist.rdata")


# Gender
names(US.Gender.dist)[2:3] <- c("ACS","MM")
US.Gender <- US.Gender.dist %>% gather(Source,Proportion,ACS:MM)
US.Gender$Gender <- paste0(toupper(substring(US.Gender$Gender,1,1)),substring(US.Gender$Gender,2))

pdf(file="USgender.pdf", width = 8, height = 8)
ggplot(US.Gender,aes(x=Gender,y=Proportion,fill=Source), color=Source) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  #geom_text(aes(label=round(count,2)),size = 9, position = position_stack(vjust = 0.9),color="black")+
  labs(title="Gender distribution of US sample")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.75)+
  theme_bw()+
  #scale_color_manual(name="", values=c("#e41a1c","#377EB8"))+
  #scale_fill_manual(name="", values=c("#e41a1c","#377EB8"))+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))
dev.off()

# Age
names(US.Age.dist) <- c("Age","ACS","MM")
US.Age <- US.Age.dist %>% gather(Source,Proportion,ACS:MM)
US.Age$Age <- factor(US.Age$Age,levels = rev(US.Age$Age[1:6]))

pdf(file="USage.pdf", width = 8, height = 8)
ggplot(US.Age,aes(x=Age,y=Proportion,fill=Source), color=Source) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  #geom_text(aes(label=round(count,2)),size = 9, position = position_stack(vjust = 0.9),color="black")+
  labs(title="Age distribution of US sample")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.6)+
  theme_bw()+
  #scale_color_manual(name="", values=c("#e41a1c","#377EB8"))+
  #scale_fill_manual(name="", values=c("#e41a1c","#377EB8"))+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))
dev.off()


# Education
names(US.Education.dist) <- c("Education","ACS","MM")
US.Education.dist$Education <- c("Bachelor Degree", "Attended College","Graduate Degree",
                            "High School Diploma","Attended High School")
US.Education <- US.Education.dist %>% gather(Source,Proportion,ACS:MM)
US.Education$Education <- factor(US.Education$Education,levels = US.Education$Education[c(3,1,2,4,5)])

pdf(file="USeducation.pdf", width = 9, height = 9)
ggplot(US.Education,aes(x=Education,y=Proportion,fill=Source), color=Source) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  #geom_text(aes(label=round(count,2)),size = 9, position = position_stack(vjust = 0.9),color="black")+
  labs(title="Education distribution of US sample")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.35)+
  theme_bw()+
  #scale_color_manual(name="", values=c("#e41a1c","#377EB8"))+
  #scale_fill_manual(name="", values=c("#e41a1c","#377EB8"))+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))
dev.off()


# Income
names(US.Income.dist) <- c("Income","ACS","MM")
US.Income.dist$Income <- gsub("above100000","100000",US.Income.dist$Income)
US.Income.dist$Income <- gsub("under5000","-1",US.Income.dist$Income)
US.Income.dist <- US.Income.dist[c(5,2,1,3,4),]
#US.Income.dist <- US.Income.dist[c(9,5,1:4,6:8),]

len <- nrow(US.Income.dist)
US.Income.dist$Income[1:len-1] <- paste0("$",
                                             as.character(format(as.numeric(US.Income.dist$Income[1:len-1])+1,big.mark=",", trim=TRUE)),
                                             " - $",as.character(format(as.numeric(US.Income.dist$Income[2:len]),big.mark=",", trim=TRUE)))
US.Income.dist$Income[len] <- paste0("More than $",as.character(format(as.numeric(US.Income.dist$Income[len])+1,big.mark=",", trim=TRUE)))
US.Income.dist$Income <- factor(US.Income.dist$Income,levels = rev(US.Income.dist$Income))

US.Income <- US.Income.dist %>% gather(Source,Proportion,ACS:MM)

pdf(file="USincome.pdf", width = 8, height = 8)
ggplot(US.Income,aes(x=Income,y=Proportion,fill=Source), color=Source) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  labs(title="Income distribution of US sample")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.35)+
  theme_bw()+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="no",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))
dev.off()


## Legend only
gg <- ggplot(US.Income,aes(x=Income,y=Proportion,fill=Source), color=Source) +  
  stat_summary(fun.y=mean,position=position_dodge(),geom="bar",width=0.6)+
  labs(title="Income distribution of US sample")+
  xlab("")+
  ylab("\nProportion")+
  coord_flip()+
  ylim(0,0.35)+
  theme_bw()+
  scale_colour_brewer(palette = "Set1")+
  scale_fill_brewer(palette = "Set1")+
  guides(fill = guide_legend(reverse = TRUE))+
  guides(color = guide_legend(reverse = TRUE))+ 
  theme_ipsum_rc(grid="Y",axis_title_just="m")+
  theme(text=element_text(size=26),legend.position="right",aspect.ratio=1/1,plot.title = element_text(size=28,hjust = 0.5),
        axis.text.y = element_text(size=22,colour = "black"),axis.title.x = element_text(size=26),
        axis.text.x = element_text(size=24,colour="black"),
        legend.text=element_text(size=16),strip.background = element_rect(color="black",fill="white"),
        panel.border = element_rect(colour = "black", fill=NA, size=1.5))


gglegend <- function(x){
  tmp <- ggplot_gtable(ggplot_build(x))
  leg <- which(sapply(tmp$grobs, function(y) y$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  return(legend)}
legend <- gglegend(gg)

pdf("Legend.pdf", width = 2, height = 2) 
grid::grid.newpage()
grid::grid.draw(legend)
dev.off() 
