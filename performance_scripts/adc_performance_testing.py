# PERFORMANCE TESTING PYTHON SCRIPT
# AUTHOR: LAURA GUTIERREZ FUNDERBURK
# SUPERVISOR: JAMIE SCOTT, FELIX BREDEN, BRIAN CORRIE
# CREATED ON: October 31, 2019
# LAST MODIFIED ON: March 23 2021

from curlairripa import *       # https://test.pypi.org/project/curlairripa/ 
import time                     # time stamps
import pandas as pd
import argparse                 # Input parameters from command line 
import os
import airr

def get_timestamp():
    """
    This function gets a time and date for test 
    
    Output:
        downloaded_at (str) date and time of test
    """
    # Get timestampt
    dates = pd.to_datetime('today')
    dates_str = str(dates)
    date_f = dates_str.split(" ")[0]
    time_f = dates_str.split(" ")[1].split(".")[0]
    downloaded_at = date_f + "_"+time_f
            
    return downloaded_at

def form_facet_query_df(query_json_raw):
    
    """
    This function takes query output for performance testing (various queries) at the facet level
    and parses it as an object of type dataframe
    
    Input:
        query_json_raw (JSON object): output obtained after performing a rearrangement facet query
    
    Output:
        json_response_df (dataframe object): json response parsed as a df, with additional information 
        such as number of repertoires and number of rearrangements
    """
    
    # Get time_stamp
    download_stamp = get_timestamp()
    
    # Test - check query is non empty
    if len(query_json_raw) != 0:
        query_json = json.loads(query_json_raw)

        #  Turn query response into pandas dataframe
        norm_facets = pd.json_normalize(query_json['Facet'])
        all_facets_count.append(norm_facets)
        if 'count' in norm_facets.keys():
            json_response_df["NumberRepertoire"] = len(norm_facets[norm_facets['count']!=0])
            json_response_df["NumberRearrangement"] = sum(norm_facets["count"])
        else:
            json_response_df["NumberRepertoire"] = 0
            json_response_df["NumberRearrangement"] =0

    # Report bogus query with -100 for repertoire and rearrangement 
    else:
        json_response_df["NumberRepertoire"] = -100
        json_response_df["NumberRearrangement"] = -100

                
    return json_response_df

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # Output Directory - where Performance test results will be stored 
    parser.add_argument(
        "base",
        help="Indicate the full path to where performance test results will be stored"
    )
    # Array with URL
    parser.add_argument(
        "ipa_arr",
        help="String containing URL to API server  (e.g. https://airr-api2.ireceptor.org)"
    )
    # Entry point
    parser.add_argument(
        "entry_point",
        help="Options: string 'rearragement' or string 'repertoire'"
    )
    
    parser.add_argument(
            "json_files",
        help="Enter full path to JSON queries"
    )

    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    # Input reading
    options = getArguments()
    output_dir = options.base
    base_url = options.ipa_arr
    entry_pt = options.entry_point
    query_files = options.json_files
    query_url = base_url + "/airr/v1/" + entry_pt
    
    # Leave static for now
    expect_pass = True
    verbose = True
    force = True

    # Ensure our HTTP set up has been done.
    initHTTP()
    # Get the HTTP header information (in the form of a dictionary)
    header_dict = getHeaderDict()
    
    # Get all JSON files
    files = []
    for r, d, f in os.walk(query_files):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))
    
    # Initialize facet count and performance results dataframes
    all_facets_count = []
    json_response_all_dfs = []
    
    # Perform query for each JSON file
    print("\nADC-API AIRR Performance Testing\n")
    
    # Check for the presence of hidden files
    for item in files:
        if "checkpoint" in item:
            continue
        else:
            
            # Load file
            query_dict = process_json_files(force,verbose,item)

            # Turn response into pandas dataframe 
            json_response_df = pd.json_normalize(query_dict)

            # Perform the query. Time it
            start_time = time.time()
            query_json_raw = processQuery(query_url, header_dict, expect_pass, query_dict, verbose, force)
            total_time = time.time() - start_time
            
            # CASE I: rearrangement query
            if entry_pt =="rearrangement":
                # Form dataframe with facet query results
                json_response_df = form_facet_query_df(query_json_raw)
        
                
            # CASE II: entry point is repertoire
            elif  entry_pt == "repertoire":
                # Test - check query is non empty
                if len(query_json_raw) != 0:
                    
                    # Load as JSON object
                    query_json = json.loads(query_json_raw)
                    
                    # Parse json response into dataframe 
                    json_response_df = pd.json_normalize(query_json)
                    json_response_df["QueryName"] = item
                    json_response_df.drop("Repertoire",1,inplace=True)
                else:
                    print("EMPTY QUERY")
            
            # Append time taken 
            json_response_df["TimeTaken(s)"] = total_time
            # Store results 
            json_response_all_dfs.append(json_response_df)        
                
            # Add time stamp
        dates = pd.to_datetime('today')
        json_response_df["Date/Time"] = dates
        json_response_df['Date/TimeConverted'] = json_response_df['Date/Time'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific')

    # Store in array for storage of all query results into single CSV
    df_list = [json_response_all_dfs[i] for i in range(len(json_response_all_dfs))]

    # Stack all results into single datafrane
    stacked = pd.concat(df_list)
    

    # Store content 
    download_stamp = get_timestamp()
    service = str(base_url.split("//")[1].split(".")[0])
    base_url_ = str(base_url.split("/")[-1])
    file_name = [output_dir,"_PerformanceTesting_" ,str(download_stamp) , "_Query_Times_" ,service , "_" , base_url_ ,  ".csv"]
    # Save file
    stacked.to_csv(("").join(file_name),sep=",")
