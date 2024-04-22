# The Moral Machine Experiment
# Edmond Awad
# Fig 4 and Fig S10-S11 (CrossCountry plots)
##############

# Set up
library(ggplot2)
library(reshape2)
library(plyr)
library(dplyr)
library(tidyr)
library(AER)
library(sandwich)
library(multiwayvcov)
library(data.table)
library(hrbrthemes)
library(extrafont)
# font_import()
# y
loadfonts()
library(ggthemes)
library(readstata13)
library(grid)

setwd("/Users/edmondawad/Dropbox (MIT)/MM_FirstBigPaper/CrossCountryPlots")

clustercolors <- c("#CC6677","#4477AA","#DDCC77")

# Load MM data
## Data that map countries to our identified clusters
data.MMclusters <- fread(input="country_cluster_map.csv")
## Data for MM distance from US
data.MMdist <- fread(input="moral_distance.csv")
names(data.MMdist) <- c("ISO3","MMdistance")
data.c.d <- merge(data.MMclusters,data.MMdist,by="ISO3",all=T)

## Data from MM: effect sizes for 9 attributes
data.mm <- fread(input="CountriesChangePr.csv")
data.mm <- data.mm[,c(1:10)]
colnames(data.mm) <- c("ISO3", "Preferenence for Inaction", "Sparing Pedestrians",
                       "Sparing the Lawful","Sparing Females","Sparing The Fit",
                       "Sparing Higher Status","Sparing the Young","Sparing More Characters",
                       "Sparing Humans")
## Merge all MM data together
data.all.mm <- merge(data.c.d,data.mm,by="ISO3",all=T)


## Data from External Source 1: Individualism, Gini (2004), RuleOfLaw (2016),  
## GDP per capita [PPP] (2017),  and Gender Gap in Educational and Health Survival score (2016)
data.ex1 <- fread(input="CrossCountryExternal1.csv")

# Merge with MM data
data.all <- merge(data.all.mm,data.ex1,by="ISO3",all=T)

## Data from External Source 2: Cultural distance from US
data.ex2 <- fread(input="CrossCountryExternal2.csv")

# Merge with MM data
data.all <- merge(data.all,data.ex2,by="Country",all=T)

data.all <- data.all[order(data.all$ISO3),]
data.all <- data.all[which(!is.na(data.all$ISO3)),]
data.all <- data.all[!duplicated(data.all$ISO3),]

# Convert to factors
data.all$Cluster <- factor(data.all$Cluster,
                           labels=c("Cluster 1 (Western)",
                                    "Cluster 2 (Eastern)",
                                    "Cluster 3 (Southern)"))

data.all$dummy <- 1


# Plotting
setwd("/Users/edmondawad/Dropbox (MIT)/MM_FirstBigPaper/CrossCountryPlots/testing")

## Figure 4.a: Correlation between Individualism and each of saving more and saving the young
adjR2p.i1 <- ddply(data.all, c("dummy"),summarize, 
                   adjr2 = round(cor.test(Individualism,`Sparing More Characters`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                   p= round(cor.test(Individualism,`Sparing More Characters`, method="spearman",exact = FALSE)$p.value,4))

adjR2p.i2 <- ddply(data.all, c("dummy"),summarize, 
                   adjr2 = round(cor.test(Individualism,`Sparing the Young`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                   p= round(cor.test(Individualism,`Sparing the Young`, method="spearman",exact = FALSE)$p.value,4))

gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(Individualism, `Sparing More Characters`))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=data.all,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.i1,aes(label=paste("rho == ", adjr2)), x=10, y=c(0.6),size=6,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.i1,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))), x=10, y=c(0.59),size=6,
            family = "Roboto Condensed")+
  xlim(0,100)+ ylim(0.35,0.62)+ theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=24, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=22),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=24), axis.title.y = element_text(size=24),strip.text.y = element_text(size=24),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

gg0 <- ggplot(filter(data.all,!is.na(Cluster)),aes(Individualism, `Sparing the Young`))+
  geom_point(aes(color = Cluster),size=1.4,shape=19)+#scale_size_area(max_size = 3)+
  #geom_text(data=data.all,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.i2,aes(label=paste("rho == ", adjr2)), x=75, y=c(0.42),size=5,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.i2,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))), x=75, y=c(0.41),size=5,
            family = "Roboto Condensed")+
  theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=14, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=12),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=14), axis.title.y = element_text(size=14),strip.text.y = element_text(size=14),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=2),strip.background = element_rect(color="black",fill="white"))


ggg <- gg+annotation_custom(ggplotGrob(gg0),xmin=46,xmax=112,ymin=0.29,ymax=0.515)

ggsave(file="Individualism.pdf",width = 7, height = 7)


## Figure 4.c: Correlation between Saving the lawful and each of GDP and Rule of Law
adjR2p.r1 <- ddply(data.all, c("dummy"),summarize, 
                   adjr2 = round(cor.test(RuleOfLaw2016,`Sparing the Lawful`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                   p= round(cor.test(RuleOfLaw2016,`Sparing the Lawful`, method="spearman",exact = FALSE)$p.value,4))

adjR2p.r2 <- ddply(data.all, c("dummy"),summarize, 
                   adjr2 = round(cor.test(log10(GDPcapPPP2017),`Sparing the Lawful`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                   p= round(cor.test(log10(GDPcapPPP2017),`Sparing the Lawful`, method="spearman",exact = FALSE)$p.value,4))



gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(RuleOfLaw2016,`Sparing the Lawful`))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=data.all,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.r1,aes(label=paste("rho == ", adjr2)), size=6, x=c(-2),y=0.46, inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.r1,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=6,x=c(-2),y=0.45, inherit.aes = FALSE,
            family = "Roboto Condensed")+
  ylim(0.09,0.48)+ 
  theme_bw()+xlab("Rule of Law")+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=24, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=22),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=24), axis.title.y = element_text(size=24),strip.text.y = element_text(size=24),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

gg0 <- ggplot(filter(data.all,!is.na(Cluster)),aes(log10(GDPcapPPP2017),`Sparing the Lawful`))+
  geom_point(aes(color = Cluster),size=1.4,shape=19)+#scale_size_area(max_size = 3)+
  #geom_text(data=data.all,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.r2,aes(label=paste("rho == ", adjr2)), size=5, x=c(3.65),y=0.465, inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.r2,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=5,x=c(3.65),y=0.46, inherit.aes = FALSE,
            family = "Roboto Condensed")+
  #ylim(0.22,0.48)+ 
  theme_bw()+xlab("Log GDP pc")+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=14, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=12),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=14), axis.title.y = element_text(size=14),strip.text.y = element_text(size=14),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=2),strip.background = element_rect(color="black",fill="white"))

ggg <- gg+annotation_custom(ggplotGrob(gg0),xmin=-0.5,xmax=2.48,ymin=0.0,ymax=0.33)

ggsave(file="RuleOfLaw.pdf", width = 7, height = 7)


## Figure 4.c: Correlation between MMdistance and Cultural distance
adjR2p.d <- ddply(data.all, c("dummy"),summarize, 
                  adjr2 = round(cor.test(CULTdistance,MMdistance, method="spearman",exact = FALSE)$estimate[[1]],2), 
                  p= round(cor.test(CULTdistance,MMdistance, method="spearman",exact = FALSE)$p.value,4))


gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(CULTdistance, MMdistance))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=filter(data.all,!is.na(Cluster)), aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, 
            family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.d,aes(label=paste("rho == ", adjr2)), size=5, x=c(0.2), y=0.4,inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.d,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=5,x=c(0.2), y=0.3,inherit.aes = FALSE,
            family = "Roboto Condensed")+
  #facet_grid(.~Yaxis,scales = "free")+
  ylab("MM distance from US")+ ylim(0,6)+ 
  xlab("Cultural distance from US")+ 
  theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=15),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=18), axis.title.y = element_text(size=18),strip.text.y = element_text(size=18),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="CultDistanceFromUS.pdf", width = 5, height = 5)




## Figure 4.d: Correlation between Saving higher status and Gini
adjR2p.g <- ddply(data.all, c("dummy"),summarize, 
                  adjr2 = round(cor.test(Gini2015,`Sparing Higher Status`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                  p= round(cor.test(Gini2015,`Sparing Higher Status`, method="spearman",exact = FALSE)$p.value,4))


gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(Gini2015, `Sparing Higher Status`))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+
  geom_text(data=filter(data.all,!is.na(Cluster)), aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, 
            family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.g,aes(label=paste("rho == ", adjr2)), size=5, x=c(50), y=0.25,inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.g,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=5,x=c(50), y=0.24,inherit.aes = FALSE,
            family = "Roboto Condensed")+
  xlab("Economic Inequality (Gini)")+ 
  theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=15),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=18), axis.title.y = element_text(size=18),strip.text.y = element_text(size=18),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="Gini.pdf", width = 5, height = 5)


## Figure 4.e: Correlation between Saving females and gender gap life expectancy
adjR2p.f <- ddply(data.all, c("dummy"),summarize, 
                  adjr2 = round(cor.test(GenderGapEducHealthSurvival2016,`Sparing Females`, method="spearman",exact = FALSE)$estimate[[1]],2), 
                  p= round(cor.test(GenderGapEducHealthSurvival2016,`Sparing Females`, method="spearman",exact = FALSE)$p.value,4))


gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(GenderGapEducHealthSurvival2016, `Sparing Females`))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=filter(data.all,!is.na(Cluster)), aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, 
            family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.f,aes(label=paste("rho == ", adjr2)), size=5, x=c(0.93), y=0.25,inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.f,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=5,x=c(0.93), y=0.24,inherit.aes = FALSE,
            family = "Roboto Condensed")+
  #facet_grid(.~Yaxis,scales = "free")+
  #ylab("AI Ethics distance from US")+ #ylim(0,6)+ 
  xlab("Gender Gap in Health and Survival")+ 
  theme_bw()+#xlim(0.92,0.98)+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1, axis.text = element_text(size=15), 
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=18), axis.title.y = element_text(size=18),strip.text.y = element_text(size=18),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="Gender.pdf", width = 5, height = 5)


## Legend only
gg <- ggplot(filter(data.all,!is.na(Cluster)),aes(Gini2015, `Sparing Higher Status`))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+
  theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="right",aspect.ratio=1/1, axis.text = element_text(size=15), 
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=18), axis.title.y = element_text(size=18),strip.text.y = element_text(size=18),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 4,byrow=TRUE))


gglegend <- function(x){
  tmp <- ggplot_gtable(ggplot_build(x))
  leg <- which(sapply(tmp$grobs, function(y) y$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  return(legend)}
legend <- gglegend(gg)

pdf("Legend.pdf", width = 2, height = 2) # Open a new pdf file
grid::grid.newpage()
grid::grid.draw(legend)
dev.off() 


# SI Figures
## Fig S10
## Fig S10 (a)

plotdata.i <- data.all[,c("ISO3","Individualism","Sparing Humans","Sparing the Young","Sparing More Characters","Cluster")]


plotdata.i2 <- plotdata.i %>% gather(Yaxis,Value,`Sparing Humans`:`Sparing More Characters`)


adjR2p.i <- ddply(plotdata.i2, c("Yaxis"), summarize, 
                  adjr2 = round(cor.test(Individualism,Value, method="spearman",exact=FALSE)$estimate[[1]],2), 
                  p= round(cor.test(Individualism,Value, method="spearman",exact=FALSE)$p.value,4))

gg <- ggplot(filter(plotdata.i2,!is.na(Cluster)),aes(Individualism, Value))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=plotdata.i2,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.i,aes(label=paste("rho == ", adjr2)), x=85, y=c(0.38,0.43,0.4),size=6,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.i,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))), x=85, y=c(0.37,0.42,0.39),size=6,
            family = "Roboto Condensed")+
  facet_grid(Yaxis~.,scales = "free")+
  ylab("")+xlim(0,100)+ theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=14, family = "Roboto Condensed"),legend.position="top",
        aspect.ratio=1/1.2,
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), 
        axis.title.x = element_text(size=20),strip.text.y = element_text(size=20),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.y=unit(0.3, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="IndividualismSI.pdf", width = 6, height = 11)


## Fig S10 (b)
plotdata.r <- data.all[,c("ISO3","Sparing Higher Status","Sparing the Lawful","Sparing Humans",
                          "Sparing More Characters","Cluster","RuleOfLaw2016")]


plotdata.r2 <- plotdata.r %>% gather(Yaxis,Value,`Sparing Higher Status`:`Sparing More Characters`)


adjR2p.r <- ddply(plotdata.r2, c("Yaxis"), summarize, 
                  adjr2 = round(cor.test(RuleOfLaw2016,Value, method="spearman",exact = FALSE)$estimate[[1]],2), 
                  p= round(cor.test(RuleOfLaw2016,Value, method="spearman",exact = FALSE)$p.value,4))

gg <- ggplot(filter(plotdata.r2,!is.na(Cluster)),aes(RuleOfLaw2016, Value))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=plotdata.r2,aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.r,aes(label=paste("rho == ", adjr2)), size=6, x=-1.5, y=c(0.25,0.39,0.41,0.45),inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.r,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=6,x=-1.5, y=c(0.24,0.38,0.405,0.44),inherit.aes = FALSE,
            family = "Roboto Condensed")+
  facet_grid(Yaxis~.,scales = "free")+
  ylab("")+ xlab("Rule of Law")+ xlim(-2,2)+ theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=12, family = "Roboto Condensed"),#legend.position="top",
        legend.position="none",aspect.ratio=1/1.2,
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), 
        axis.title.x = element_text(size=20),strip.text.y = element_text(size=20),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.y=unit(0.3, "lines"),
        legend.text=element_text(size=10),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 4,byrow=TRUE))

ggsave(file="RuleOfLawSI.pdf", width = 6, height = 13)


## Fig S11
## Fig S11 (a): Ruler for MM distance
plotdata.ruler <- data.all[,c("ISO3", "MMdistance", "Cluster")]
plotdata.ruler <- na.omit(plotdata.ruler)
plotdata.ruler <- setorder(plotdata.ruler,MMdistance)
plotdata.ruler <- plotdata.ruler %>% mutate(
  DnD = MMdistance - c(0,MMdistance[1:(nrow(plotdata.ruler)-1)]),
  Vertical = 0)

newV <- function(DD,V.m1,csize){
  if (DD < csize) return((V.m1+1)%%15)
  else return(0)
}
for(i in 2:nrow(plotdata.ruler)){
  plotdata.ruler$Vertical[i] <- newV(plotdata.ruler$DnD[i],plotdata.ruler$Vertical[i-1],0.1)
}

plotdata.ruler$Vertical <- ifelse(plotdata.ruler$Vertical%%2==0,-plotdata.ruler$Vertical,plotdata.ruler$Vertical+1)

#plotdata.ruler <- plotdata.ruler[which(plotdata.ruler$CountryISO3!="REU"),]

gg <- ggplot(filter(plotdata.ruler,!is.na(Cluster)),aes(MMdistance,Vertical))+
  geom_segment(aes(x=MMdistance,xend=MMdistance,yend=Vertical),y=0, color="grey95", size=0.6)+
  geom_hline(yintercept=0, color="black", size=0.7)+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=filter(plotdata.ruler,!is.na(Cluster)), aes(label=ISO3), size = 1.9,
            nudge_x = 0,nudge_y = 0, family = "Roboto Condensed",color="white")+
  xlab("MM distance from US")+ ylab("")+ ylim(-17,17)+
  scale_color_manual(values=clustercolors)+
  scale_x_continuous(breaks=seq(0,8))+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="top",aspect.ratio=1/2.5,
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(hjust = 0.5),
        axis.title.x = element_text(size=20),strip.text.y = element_text(size=18),axis.text.y=element_blank(),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(0.3, "lines"),
        legend.text=element_text(size=14),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="Ruler.pdf", width = 8, height = 5)


## Fig S11 (b)
plotdata.d <- data.all[,c(c("ISO3","MMdistance","Genetic Distance from US","CULTdistance","Cluster"))]
names(plotdata.d)[4] <- "Cultural Distance from US"
plotdata.d2 <- plotdata.d %>% gather(Yaxis,Value,`Genetic Distance from US`:`Cultural Distance from US`)

plotdata.d2 <- plotdata.d2[which(!is.na(plotdata.d2$MMdistance)),]

adjR2p.d <- ddply(plotdata.d2, c("Yaxis"), summarize, 
                  adjr2 = round(cor.test(MMdistance,Value, method="spearman",exact = FALSE)$estimate[[1]],2), 
                  p= round(cor.test(MMdistance,Value, method="spearman",exact = FALSE)$p.value,4))

gg <- ggplot(filter(plotdata.d2,!is.na(Cluster)),aes(Value, MMdistance))+
  geom_point(aes(color = Cluster),size=4.2,shape=19)+#scale_size_area(max_size = 3)+
  geom_text(data=filter(plotdata.d2,!is.na(Cluster)), aes(label=ISO3), size = 1.9,nudge_x = 0,nudge_y = 0, 
            family = "Roboto Condensed",color="white")+
  geom_smooth(method = "lm", se = F,color="grey50",size=0.5)+
  geom_text(data=adjR2p.d,aes(label=paste("rho == ", adjr2)), size=6, x=c(0.2,0.04), y=0.4,inherit.aes = FALSE,
            family = "Roboto Condensed",parse=TRUE)+
  geom_text(data=adjR2p.d,aes(label=ifelse(p==0,"\n p < 1e-04",paste("\n p = ", p))),size=6,x=c(0.2,0.04), y=0.3,inherit.aes = FALSE,
            family = "Roboto Condensed")+
  facet_grid(.~Yaxis,scales = "free")+
  ylab("MM distance from US")+ xlab("")+ ylim(0,6)+ 
  theme_bw()+
  scale_color_manual(values=clustercolors)+
  theme_ipsum_rc(grid="XY",axis_title_just="m")+
  theme(text=element_text(size=18, family = "Roboto Condensed"),legend.position="no",aspect.ratio=1/1,
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(), strip.text.x = element_text(size=20,hjust = 0.5),
        axis.title.y = element_text(size=24),strip.text.y = element_text(size=20),
        panel.border=element_rect(color="grey20",fill=NA), panel.spacing.x=unit(1, "lines"),
        legend.text=element_text(size=12),strip.background = element_rect(color="black",fill="white"))+
  guides(color = guide_legend(nrow = 3,byrow=TRUE))

ggsave(file="DistanceFromUS.pdf", width = 8.5, height = 6)




