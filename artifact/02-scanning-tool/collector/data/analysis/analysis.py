from collections import Counter
import os

def main():
    from config import config
    import scripts.datacleaning
    import scripts.analysis
    import scripts.figures

    ####
    #
    # General figures
    #
    ####
    

    ## Analysis
    config.DATA_BASEDIR = "./logdir_current/"
    config.RESULTS_DIR =  "./logdir_current/results/"
    config.FIGURES_DIR =  "./logdir_current/figures/"
    config.KEY = "current"

    try:
        os.mkdir(config.RESULTS_DIR)
    except:
        pass
    try:
        os.mkdir(config.FIGURES_DIR)
    except:
        pass

    ####
    #
    # Datacleaning
    #
    ####
    # Read the domainfile log and create a list of unique domains and skipped wirldcards
    scripts.datacleaning.domainfile_log_to_unique_domainlist_with_count()

    # Read the query log and analyze its (error) messages
    scripts.datacleaning.querylog_to_counted_messages()

    # Read the parser log and structure its data
    scripts.datacleaning.parserlog_to_structured_data()

    # Read the server log and structure its data
    scripts.datacleaning.server_to_structured_data()

    ####
    #
    # Analysis
    #
    ####
    # Count the number of scanned domains
    scripts.analysis.domainfile_general_numbers_scanned_domains()
    # Count the errors and successful SSHFP queries:
    scripts.analysis.query_log_analysis()
    # Analyze the parser errors and successfully parsed SSHFP entries
    scripts.analysis.parserlog_analysis()
    # 
    scripts.analysis.serverlog_analysis()

    scripts.analysis.notification_analysis()




if __name__ == "__main__":
    main()
