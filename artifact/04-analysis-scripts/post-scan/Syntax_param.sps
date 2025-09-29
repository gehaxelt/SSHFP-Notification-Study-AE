* Encoding: UTF-8.
DATASET ACTIVATE DataSet7.

/* recode variable group

/* all groups
RECODE group ('U1'=1) ('U2'=2) ('U1_same'=3) ('U2_same'=4) ('U1_diff'=5) ('U2_diff'=6) 
    INTO group_numerical.
EXECUTE.

/* all sender
RECODE group ('U1'=1) ('U2'=2) ('U1_same'=1) ('U2_same'=2) ('U1_diff'=1) ('U2_diff'=2) 
    INTO group_sender.
EXECUTE.

/* all tool
RECODE group ('U1'=1) ('U2'=1) ('U1_same'=2) ('U2_same'=2) ('U1_diff'=2) ('U2_diff'=2) 
    INTO group_tool.
EXECUTE.

/* all tool same vs. tool different
RECODE group ('U1'=1) ('U2'=1) ('U1_same'=2) ('U2_same'=2) ('U1_diff'=3) ('U2_diff'=3) 
    INTO group_toolall.
EXECUTE.

/* Normalverteilung bestimmen
EXAMINE VARIABLES=survival_time BY group
  /PLOT BOXPLOT NPPLOT
  /COMPARE GROUPS
  /STATISTICS DESCRIPTIVES
  /CINTERVAL 95
  /MISSING LISTWISE
  /NOTOTAL.
EXECUTE.

/* ANOVA KIT vs. TUB
ONEWAY survival_time BY group_sender
  /ES=OVERALL
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH 
  /PLOT MEANS
  /MISSING ANALYSIS
  /CRITERIA=CILEVEL(0.95)
  /POSTHOC=TUKEY BONFERRONI GH ALPHA(0.05).
EXECUTE.

/* ANOVA tool vs. no tool
ONEWAY survival_time BY group_tool
  /ES=OVERALL
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH 
  /PLOT MEANS
  /MISSING ANALYSIS
  /CRITERIA=CILEVEL(0.95)
  /POSTHOC=TUKEY BONFERRONI GH ALPHA(0.05).
EXECUTE.

/* ANOVA all groups
ONEWAY survival_time BY group_numerical
  /ES=OVERALL
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH 
  /PLOT MEANS
  /MISSING ANALYSIS
  /CRITERIA=CILEVEL(0.95)
  /POSTHOC=TUKEY BONFERRONI GH ALPHA(0.05).
EXECUTE.

/* ANOVA tool vs. tool same vs. tool different
ONEWAY survival_time BY group_toolall
  /ES=OVERALL
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH 
  /PLOT MEANS
  /MISSING ANALYSIS
  /CRITERIA=CILEVEL(0.95)
  /POSTHOC=TUKEY BONFERRONI GH ALPHA(0.05).
EXECUTE.

/* 2-factor ANOVA sender vs. tool 3
UNIANOVA survival_time BY group_sender group_toolall
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /POSTHOC=group_sender group_toolall(TUKEY BONFERRONI) 
  /PLOT=PROFILE(group_sender*group_toolall) TYPE=LINE ERRORBAR=NO MEANREFERENCE=NO YAXIS=AUTO
  /PRINT DESCRIPTIVE HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=group_sender group_toolall group_sender*group_toolall.
EXECUTE.

/* 2-factor ANOVA sender vs. tool 6
UNIANOVA survival_time BY group_sender group_numerical
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /POSTHOC=group_sender group_numerical(TUKEY BONFERRONI) 
  /PLOT=PROFILE(group_sender*group_numerical) TYPE=LINE ERRORBAR=NO MEANREFERENCE=NO YAXIS=AUTO
  /PRINT DESCRIPTIVE HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=group_sender group_numerical group_sender*group_numerical.
EXECUTE.


