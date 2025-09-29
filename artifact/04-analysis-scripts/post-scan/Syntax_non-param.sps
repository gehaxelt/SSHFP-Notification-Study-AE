* Encoding: UTF-8.
DATASET ACTIVATE DataSet2.

/* recode variable group
RECODE group ('U1'=1) ('U2'=2) ('U1_same'=3) ('U2_same'=4) ('U1_diff'=5) ('U2_diff'=6) 
    INTO group_numerical.
EXECUTE.

RECODE group ('U1'=1) ('U2'=2) ('U1_same'=1) ('U2_same'=2) ('U1_diff'=1) ('U2_diff'=2) 
    INTO group_sender.
EXECUTE.

RECODE group ('U1'=1) ('U2'=1) ('U1_same'=2) ('U2_same'=2) ('U1_diff'=2) ('U2_diff'=2) 
    INTO group_tool.
EXECUTE.

RECODE group ('U1'=1) ('U2'=1) ('U1_same'=2) ('U2_same'=2) ('U1_diff'=3) ('U2_diff'=3) 
    INTO group_toolall.
EXECUTE.

DATASET ACTIVATE DataSet3.
/* crosstabs Status vs. Gruppen
CROSSTABS
  /TABLES=Status BY group_numerical group_sender group_tool group_toolall
  /FORMAT=AVALUE TABLES
  /STATISTICS=CHISQ CC PHI CORR 
  /CELLS=COUNT EXPECTED BPROP 
  /COUNT ROUND CELL
  /BARCHART.

/* Interaction groups
CROSSTABS
  /TABLES=group_sender BY group_numerical group_tool group_toolall
  /FORMAT=AVALUE TABLES
  /STATISTICS=CHISQ CC PHI CORR 
  /CELLS=COUNT EXPECTED BPROP 
  /COUNT ROUND CELL
  /BARCHART.
