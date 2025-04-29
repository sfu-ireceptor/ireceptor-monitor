import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import sys
import argparse
import numpy as np
import plotly.io as pio
import plotly.express as px
import sys
import csv
import math

csv.field_size_limit(sys.maxsize)

def clean_df(df):
     #Remove cols
    if "Repertoire" in df.columns:
        df.drop("Repertoire",1,inplace=True)
    if "Unnamed: 0" in df.columns:
        df.drop(['Unnamed: 0'], 1,inplace=True)
    # Add variable num
    #if "Query#" not in df.columns:
    #    df['Query#'] = [i for i in range(df.shape[0])]
    return df

def plot_performance(df,name,output_dir,subfield):

    full_fig  = px.line(df,
                   y="TimeTaken(s)",
                   x="Date/TimeConverted",title="Time taken per query",facet_col=subfield,color="QueryName(shortened)",
                   labels={"Date/TimeConverted":"Date"},range_y=[0,10])
    # Get rid of facet name (from: 
    #     https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles)
    full_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))


    pio.write_html(full_fig,output_dir+str(name) + "_TimeSeries_.html",
                      auto_open=False)

def parse_df_content(df,s_date,e_date):

    # Concatenate array with df
    new_df = pd.concat(df)
    # Sort values by date and time
    new_df.sort_values(by=['Date/TimeConverted'],inplace=True)
    # Get only desired dates
    new_df = new_df[(new_df['Date/TimeConverted']>=s_date) & (new_df['Date/TimeConverted']<=e_date)]
    # Remove NA values
    new_df.dropna(subset=['QueryName'], inplace=True)
    # Query processing - query name is a path and the query file contains pass.
    # We want to replace everything except the file name.
    query_regex = r'(^.*pass)'
    new_df['QueryName(shortened)'] = new_df['QueryName'].str.replace(query_regex,"pass",regex=True).to_list()
    

    #new_df['QueryName(shortened)'] = new_df['QueryName'].str.split(pat="/")[-1]
    #new_df['QueryName(shortened)'] = new_df['QueryName'].str.split(pat="/").to_list()
    return new_df


def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    # Output results directory
    parser.add_argument("path")
    # Start Date
    parser.add_argument("s_date")
    # End date
    parser.add_argument("e_date")
    #Output dir
    parser.add_argument("output_dir")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")
    # Unified scale flag
    parser.add_argument(
        "-s",
        "--scale",
        action="store_true",
        help="Scale the graphs so they are all on the same y-axis scale.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Read arguments
    options = getArguments()

    path = options.path
    s_date = options.s_date
    e_date = options.e_date
    output_dir = options.output_dir

    # Get date in timestamp format.
    date_format = "%Y-%m-%d"
    datetime_object = datetime.datetime.strptime(str(s_date), date_format)
    s_timestamp = datetime_object.timestamp()
    datetime_object = datetime.datetime.strptime(str(e_date), date_format)
    e_timestamp = datetime_object.timestamp()

    # Get the files from within the date range
    files = []
    for item in os.listdir(path):
        file_path = os.path.join(path, item)
        if os.path.isfile(file_path) and ".csv" in item:
            file_timestamp = os.path.getmtime(file_path)
            if file_timestamp >= s_timestamp and file_timestamp <= e_timestamp:
                files.append(file_path)


    ireceptor_df = []
    covid_df = []
    t1d_df = []
    vdjserver_df = []
    roche_df = []
    airr_seq_df = []
    scireptor_df = []
    muenster_df = []
    external_df = []
    for i in range(len(files)):

      try:
        df = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
      except:
        print("Could not read file %s"%(files[i]))
      else:
        if "ipa" in files[i] and "covid" not in files[i]:
            # File names are of the form:
            # _PerformanceTesting_2025-04-29_19:03:10_Query_Times_ipa2_ipa2.ireceptor.org.csv
            # We parse the file name to extract the repository. First, get 
            # the file name (the last field after /), then split on the
            # repository with csv extension and discard (leaving the repository
            # name part. Then split on _ and grab the last or second to last 
            # item which is the short name of the repository.
            df["IPA#"] = files[i].split("/")[-1].split(".ireceptor.org.csv")[0].split("_")[-1]
            # Remove odd col, remove Repertoire col, add query col
            clean_df(df)
            # Save new file
            df.to_csv(files[i])
            # Add to list of data frames
            ireceptor_df.append(df)
        if "vdjserver" in files[i]:
            if "QueryName" in df.columns:
                df["IPA#"] = files[i].split("/")[-1].split("vdjserver.org.csv")[0].split("_")[-2]
                df["Service"]="VDJServer (US)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(df)
                # Save new file
                df.to_csv(files[i])
                vdjserver_df.append(df)
            else:
                continue
        if "airr-seq" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("airr-seq.vdjbase.org.csv")[0].split("_")[-2]
            df["Service"]="VDJBase (Israel)"
            # Remove odd col, remove Repertoire col, add query col
            clean_df(df)
            # Save new file
            df.to_csv(files[i])
            airr_seq_df.append(df)
        if "covid" in files[i]:
            df['IPA#'] = files[i].split("/")[-1].split("ireceptor.org.csv")[0].split("_")[-2]
            # Remove odd col, remove Repertoire col, add query col
            clean_df(df)
            # Save new file
            df.to_csv(files[i])
            covid_df.append(df)
        if "t1d" in files[i]:
            df['IPA#'] = files[i].split("/")[-1].split("ireceptor.org.csv")[0].split("_")[-2]
            # Remove odd col, remove Repertoire col, add query col
            clean_df(df)
            # Save new file
            df.to_csv(files[i])
            t1d_df.append(df)
        if "scireptor" in files[i]:
            if "QueryName" in df.columns:
                df["IPA#"] = files[i].split("/")[-1].split("scireptor.dkfz.de.csv")[0].split("_")[-2]
                df["Service"]="sciReptor (Germany)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(df)
                # Save new file
                df.to_csv(files[i])
                scireptor_df.append(df)
        elif "muenster" in files[i]:
            if "QueryName" in df.columns:
                df["IPA#"] = files[i].split("/")[-1].split("agschwab.uni-muenster.de.csv")[0].split("_")[-2]
                df["Service"]="Meunster (Germany)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(df)
                # Save new file
                df.to_csv(files[i])
                muenster_df.append(df)
        elif "roche" in files[i]:
            if "QueryName" in df.columns:
                df["IPA#"] = files[i].split("/")[-1].split("roche-airr.ireceptor.org.csv")[0].split("_")[-2]
                df["Service"]="Roche/KCL (Canada)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(df)
                # Save new file
                df.to_csv(files[i])
                roche_df.append(df)
            else:
                continue

    # Process each dataframe
    ireceptor_full_df = parse_df_content(ireceptor_df,s_date,e_date)
    covid_full_df = parse_df_content(covid_df,s_date,e_date)
    t1d_full_df = parse_df_content(t1d_df,s_date,e_date)

    vdjserver_full_df = parse_df_content(vdjserver_df,s_date,e_date)
    airr_full_df = parse_df_content(airr_seq_df,s_date,e_date)
    scireptor_full_df = parse_df_content(scireptor_df,s_date,e_date)
    muenster_full_df = parse_df_content(muenster_df,s_date,e_date)
    roche_full_df = parse_df_content(roche_df,s_date,e_date)
    #external_full_df = pd.concat([vdjserver_full_df,airr_full_df,scireptor_full_df, roche_full_df, muenster_full_df])
    external_full_df = pd.concat([airr_full_df,scireptor_full_df, roche_full_df, muenster_full_df])

    # Generate plots
    external_full_df.to_csv(output_dir + "fullresults.csv",sep=",")
    plot_performance(ireceptor_full_df,"iReceptor",output_dir,"IPA#")
    plot_performance(covid_full_df,"COVID19",output_dir,"IPA#")
    plot_performance(t1d_full_df,"T1D",output_dir,"IPA#")
    plot_performance(external_full_df,"ExternalServices",output_dir,"Service")
