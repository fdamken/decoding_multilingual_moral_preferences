# This code contains last minute cosmetic changes to Fig 2 (a), Extended Data Fig1-3, and Extended Data Fig 7(e)
# Changes are mainly on re-labeling and there is one re-ordering of presentation of attribute "Law"

facs <- c("Preference for inaction\n [Interventionism]",
          "Sparing pedestrians\n [Relation to AV]",
          "Sparing the lawful\n[Law]",
          "Sparing females\n [Gender]",
          "Sparing the fit\n [Fitness]",
          "Sparing higher status\n [Social Status]",
          "Sparing the younger\n [Age]",
          "Sparing more characters\n [No. Characters]",
          "Sparing humans\n [Species]")

PlotAndSave.Split <- function(plotdata, AttrLabel, isMainFig, filename) {
  gg <- ggplot(plotdata, aes(Label, Estimates, color = Attribute)) +
    geom_hline(yintercept = 0, color = "black", size = 0.7) +
    geom_crossbar(aes(ymin = Estimates - 1.96 * se, ymax = Estimates + 1.96 * se),
                  position = position_dodge(.9), size = 0.7,
                  fatten = 1.5, width = .8) +
    coord_flip() +
    labs(title = "Average Marginal Causal Effect (AMCE)",
         color = AttrLabel) +
    xlab("") +
    ylab(expression(paste("\n ", Delta, " Pr"))) +
    ylim(0, 0.8) +
    scale_color_brewer(palette = "Set1") +
    guides(fill = guide_legend(reverse = TRUE)) +
    theme_bw() +
    theme(text = element_text(size = 15), legend.position = "right",
          aspect.ratio = 1 / 2, axis.text.y = element_text(hjust = 0, color = "black"),
          legend.text = element_text(size = 8),
          panel.border = element_rect(colour = "black", fill = NA, size = 1.5))
  if (isMainFig)
    ggsave(file = paste0(filename, gsub(" ", "", AttrLabel), ".pdf"), width = 12, height = 6)
  else
    ggsave(file = paste0(filename, gsub(" ", "", AttrLabel), "SI.pdf"), width = 12, height = 6)
}

r = 9

# Extended Data Figure 2 reproduced (changed labels)
filename <- "RobustnessExternal"
# Description
AttrLabel <- "Description is"
load("plotdataSIRobustExternalDescription.rdata")
plotdata$Attribute <- ifelse(plotdata$Attribute == "1", "seen", "not seen")
PlotAndSave.Split(plotdata, AttrLabel, F, filename)

# Device
AttrLabel <- "Device"
load("plotdataSIRobustExternalTemplate.rdata")
PlotAndSave.Split(plotdata, AttrLabel, F, filename)

# Dataset
AttrLabel <- "Dataset"
load("plotdataSIRobustExternalAllDatasets.rdata")
plotdata.main.alldatasets$Label <- rep(facs, 3)
plotdata.main.alldatasets$Label <- factor(plotdata.main.alldatasets$Label, as.ordered(plotdata.main.alldatasets$Label[match(sort(plotdata.main.alldatasets$Estimates[1:r]), plotdata.main.alldatasets$Estimates[1:r])]))
plotdata.main.alldatasets$Label <- factor(plotdata.main.alldatasets$Label, levels = rev(levels(plotdata.main.alldatasets$Label)))
PlotAndSave.Split(plotdata.main.alldatasets, AttrLabel, F, filename)


PlotAndSave.Split.Order <- function(plotdata, AttrLabel, isMainFig, filename) {
  gg <- ggplot(plotdata, aes(Attribute, Estimates)) +
    geom_hline(yintercept = 0, color = "black", size = 0.7) +
    geom_crossbar(aes(ymin = Estimates - 1.96 * se, ymax = Estimates + 1.96 * se),
                  position = position_dodge(.9), size = 0.7,
                  fatten = 1.5, width = .8, color = "black") +
    coord_flip() +
    facet_wrap(~Label) +
    labs(title = "Average Marginal Causal Effect (AMCE)") +
    xlab("Scenario Order") +
    ylab(expression(paste("\n ", Delta, " Pr"))) +
    ylim(0, 0.95) +
    scale_fill_brewer(palette = "Set1") +
    guides(fill = guide_legend(reverse = TRUE)) +
    theme_bw() +
    theme(text = element_text(size = 13), legend.position = "right",
          aspect.ratio = 0.85 / 1, axis.text.y = element_text(color = "black"),
          legend.text = element_text(size = 7),
          panel.border = element_rect(colour = "black", fill = NA, size = 1.5))
  if (isMainFig)
    ggsave(file = paste0(filename, gsub(" ", "", AttrLabel), ".pdf"), width = 12, height = 9)
  else
    ggsave(file = paste0(filename, gsub(" ", "", AttrLabel), "SI.pdf"), width = 12, height = 9)

}

# Extended Data Figure 1 reproduced (changed labels)
filename <- "RobustnessInternal"
## Scenario Order
AttrLabel <- "Scenario Order"
load("plotdataSIRobustInternalScenarioOrder.rdata")
PlotAndSave.Split.Order(plotdata, AttrLabel, F, filename)

## Profile order
AttrLabel <- "Profile is on"
load("plotdataSIRobustInternalProfileOrder.rdata")
plotdata$Attribute <- ifelse(plotdata$Attribute == "1", "left", "right")
PlotAndSave.Split(plotdata, AttrLabel, F, filename)

## Proportions
AttrLabel <- "Distribution"
load("plotdataSIRobustTheoActu.rdata")
plotdata.main.TheoActu$Attribute <- gsub(" Distribution", "", plotdata.main.TheoActu$Attribute)
plotdata.main.TheoActu$Label <- rep(facs, 2)
plotdata.main.TheoActu$Label <- factor(plotdata.main.TheoActu$Label, as.ordered(plotdata.main.TheoActu$Label[match(sort(plotdata.main.TheoActu$Estimates[1:r]), plotdata.main.TheoActu$Estimates[1:r])]))
plotdata.main.TheoActu$Label <- factor(plotdata.main.TheoActu$Label, levels = rev(levels(plotdata.main.TheoActu$Label)))
PlotAndSave.Split(plotdata.main.TheoActu, AttrLabel, F, filename)


# Extended Data Figure 7(e) reproduced (changed labels)
filename <- "ExtraRR"
AttrLabel <- "Stratification"
load("plotdataSIpoststratification.rdata")
plotdata.main.strat$Label <- rep(facs, 2)
plotdata.main.strat$Label <- factor(plotdata.main.strat$Label, as.ordered(plotdata.main.strat$Label[match(sort(plotdata.main.strat$Estimates[1:r]), plotdata.main.strat$Estimates[1:r])]))
plotdata.main.strat$Label <- factor(plotdata.main.strat$Label, levels = rev(levels(plotdata.main.strat$Label)))
PlotAndSave.Split(plotdata.main.strat, AttrLabel, F, filename)


# Extended Data Figure 3 reproduced (changed labels, moved 'Law' attribute raw down)
load("plotdataUserGender.rdata")
load("plotdataUserAge.rdata")
load("plotdataUserPolitical.rdata")
load("plotdataUserReligious.rdata")
load("plotdataUserIncome.rdata")
load("plotdataUserEducation.rdata")

#Fix order
plotdata.UserGender$Label <- factor(plotdata.UserGender$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))
plotdata.UserAge$Label <- factor(plotdata.UserAge$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))
plotdata.UserPolitical$Label <- factor(plotdata.UserPolitical$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))
plotdata.UserReligious$Label <- factor(plotdata.UserReligious$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))
plotdata.UserIncome$Label <- factor(plotdata.UserIncome$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))
plotdata.UserEducation$Label <- factor(plotdata.UserEducation$Label, as.ordered(levels(plotdata.main.alldatasets$Label)))

## Plot them
PlotAndSave.Split(plotdata.UserGender, "User Gender", F, "Inter")
PlotAndSave.Split(plotdata.UserAge, "User Age", F, "Inter")
PlotAndSave.Split(plotdata.UserPolitical, "User Political Views", F, "Inter")
PlotAndSave.Split(plotdata.UserReligious, "User Religious Views", F, "Inter")
PlotAndSave.Split(plotdata.UserIncome, "User Income", F, "Inter")
PlotAndSave.Split(plotdata.UserEducation, "User Education", F, "Inter")


# Figure 2(a) reproduced (removed circles from main effects, added x-axis ticks)
load("plotdatamain.rdata")
load("plotdatautil.rdata")

PlotAndSave <- function(plotdata.main, isMainFig, filename, plotdata.Util) {
  yticks <- seq(0.0, 0.8, 0.2)
  util.x <- which(order(plotdata.main$Label) == 8) + 0.2
  alphas <- rep(.7, 9)
  alphas[which(order(plotdata.main$Label) == 8)] <- 0
  gg <- ggplot(plotdata.main, aes(x = Label, y = Estimates)) +
    geom_hline(yintercept = 0, color = "black", size = 0.7) +
    geom_col(width = .5, fill = "#0077ad", alpha = alphas) +
    geom_col(data = plotdata.util, width = .5, fill = "#0077ad", alpha = .7, aes(y = max(Estimates))) +
    geom_point(data = plotdata.util, color = "#49c6ff", size = 5.5, shape = 21, fill = "white", stroke = 2) +
    geom_text(data = plotdata.util, aes(label = as.character(c(1:4)), y = Estimates), size = 3, color = "#37a2ef") +
    geom_point(data = plotdata.main[which(plotdata.main$Label == "No. Characters"),], size = 5.5, shape = 21, color = "#0077ad", fill = "white", stroke = 2) +
    coord_flip() +
    labs(title = "Preference in favor of the choice on the right side") +
    xlab("") +
    ylab(expression(paste("\n ", Delta, " Pr"))) +
    scale_y_continuous(limits = c(-0.2, 0.9), breaks = yticks, labels = sapply(yticks, function(z) return(ifelse(z < 0, "", ifelse(z > 0, paste0("+", as.character(z)), "no change"))))) +
    theme_bw() +
    theme_ipsum_rc(grid = "Y", axis_title_just = "m") +
    theme(text = element_text(size = 20), axis.ticks.x = element_line(size = 0.7),
          legend.position = "right", axis.ticks.length = unit(-0.2, "cm"),
          axis.text.x = element_text(margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")),
          aspect.ratio = 1 / 1.8,
          axis.title.x = element_text(size = 20),
          axis.text.y = element_text(hjust = 0, color = "black", margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")),
          legend.text = element_text(size = 8),
          panel.border = element_rect(colour = "black", fill = NA, size = 1.5))

  ggsave(file = paste0(filename, ".pdf"), width = 12, height = 6)

}

PlotAndSave(plotdata.main, T, "MainChangePr", plotdata.util)
