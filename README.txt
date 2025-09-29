SSHFP Notification Study
===========================

This repository contains the code and analysis scripts for our SSHFP Notification Study and publication "Fix it - If you Can! Towards Understanding the Impact of Tool Support and Domain Owners’ Reactions to SSHFP Misconfigurations", published in TBA [0].

# 1. Domain collection

Our analysis required a large dataset of domains to analyze for SSHFP misconfigurations. We used several datasets to compile such a dataset for German domains.

Find more information the domain collection's README.

# 2. Scanning Tool

This folder contains the scanning tool originally developed by Neef et al. [1], which we modified to suit our needs. 
The tool can be used to scan a list of domains for SSHFP misconfigurations. 
After performing the analysis of the observed SSHFP entries and corresponding SSH servers, the result will include a list of domains and their type of misconfiguration (e.g., missing DNS or Mismatching fingerprints).

Find more information in the scanning tool's README.

# 3. Selftest Tool

This folder contains the selftest tool which we developed for our notification study to allow affected users to verify their misconfiguration and mitigiation of this issue.

Find more information in the selftest tool's README.

# 4. Analysis Scripts

In order to analyze our data from the scanning tool and selftest tool, we developed several scripts.

Find more information about the scripts and their functionality in the analysis script's README.

# Comprehensiveness

As a note to reviewers: 
Since some scripts and intermediate datasets pose a risk of deanonymization due to their specificity, they cannot be shared with the reviewers. 
However, we share the relevant and interesting code and ground-truth data (e.g. the scanning-tool, selftest-tool, domain datasets used as the basis), as well as dummy datasets where necessary, to provide the most relevant information to reproduce our work. 
The excluded scripts and datasets are primarily related to the post-experiment analysis, which means the data collection and scanning is not affected by data being anonymized.

# References

- [0] TBA
- [1] https://link.springer.com/chapter/10.1007/978-3-031-20974-1_4