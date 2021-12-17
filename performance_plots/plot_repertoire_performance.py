import pandas as pd
import matplotlib.pyplot as plt
import os
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

    files = []
        # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                files.append(os.path.join(r, file))

    ireceptor_df = []
    covid_df = []
    vdjserver_df = []
    irec_df = []
    airr_seq_df = []
    scireptor_df = []
    nicd_df = []
    external_df = []
    for i in range(len(files)):

        #print(files[i])
        if "ipa" in files[i] and "covid" not in files[i]:
            ireceptor = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            ireceptor["IPA#"] = files[i].split("/")[-1].split(".ireceptor.org.csv")[0].split("_")[-1]
            # Remove odd col, remove Repertoire col, add query col
            clean_df(ireceptor)
            # Save new file
            ireceptor.to_csv(files[i])
            # Add to list of files
            ireceptor_df.append(ireceptor)
            #print("Ireceptor")
        if "vdjserver" in files[i]:
            vdj = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            if "QueryName" in vdj.columns:
                vdj["IPA#"] = files[i].split("/")[-1].split("vdjserver.org.csv")[0].split("_")[-2]
                vdj["Service"]="VDJServer (US)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(vdj)
                # Save new file
                vdj.to_csv(files[i])
                vdjserver_df.append(vdj)
            else:
                continue
        if "airr-seq" in files[i]:
            airrseq = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            airrseq["IPA#"] = files[i].split("/")[-1].split("airr-seq.vdjbase.org.csv")[0].split("_")[-2]
            airrseq["Service"]="VDJBase (Israel)"
            # Remove odd col, remove Repertoire col, add query col
            clean_df(airrseq)
            # Save new file
            airrseq.to_csv(files[i])
            airr_seq_df.append(airrseq)
        if "covid" in files[i]:
            covid =  pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            covid['IPA#'] = files[i].split("/")[-1].split("ireceptor.org.csv")[0].split("_")[-2]
            # Remove odd col, remove Repertoire col, add query col
            clean_df(covid)
            # Save new file
            covid.to_csv(files[i])
            covid_df.append(covid)
        if "scireptor" in files[i]:
            #scireptor =  pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            #scireptor['IPA#'] = files[i].split("/")[-1].split("scireptor.dkfz.de.csv")[0].split("_")[-2]
            ## Remove odd col, remove Repertoire col, add query col
            #clean_df(scireptor)
            ## Save new file
            #scireptor.to_csv(files[i])
            #scireptor_df.append(scireptor)
            scireptor = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            if "QueryName" in scireptor.columns:
                scireptor["IPA#"] = files[i].split("/")[-1].split("scireptor.dkfz.de.csv")[0].split("_")[-2]
                scireptor["Service"]="sciReptor (Germany)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(scireptor)
                # Save new file
                scireptor.to_csv(files[i])
                scireptor_df.append(scireptor)
        elif "154.127.124.38:2222.csv" in files[i]:
            nicd = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            if "QueryName" in nicd.columns:
                nicd["IPA#"] = files[i].split("/")[-1].split("154.127.124.38:2222.csv")[0].split("_")[-2]
                nicd["Service"]="NICD (South Africa)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(nicd)
                # Save new file
                nicd.to_csv(files[i])
                nicd_df.append(nicd)
        elif "irec_irec" in files[i]:
            irec_irec = pd.read_csv(files[i],sep=',', engine='python' ,encoding='utf-8', error_bad_lines=False)
            if "QueryName" in irec_irec.columns:
                irec_irec["IPA#"] = files[i].split("/")[-1].split("irec.")[0].split("_")[-2]
                irec_irec["Service"]="i3 Lab (France)"
                # Remove odd col, remove Repertoire col, add query col
                clean_df(irec_irec)
                # Save new file
                irec_irec.to_csv(files[i])
                irec_df.append(irec_irec)
            else:
                continue

    # Process each dataframe
    ireceptor_full_df = parse_df_content(ireceptor_df,s_date,e_date)
    covid_full_df = parse_df_content(covid_df,s_date,e_date)

    vdjserver_full_df = parse_df_content(vdjserver_df,s_date,e_date)
    airr_full_df = parse_df_content(airr_seq_df,s_date,e_date)
    irec_full_df = parse_df_content(irec_df,s_date,e_date)
    scireptor_full_df = parse_df_content(scireptor_df,s_date,e_date)
    nicd_full_df = parse_df_content(nicd_df,s_date,e_date)
    external_full_df = pd.concat([vdjserver_full_df,airr_full_df,scireptor_full_df, irec_full_df, nicd_full_df])

    # Generate plots
    external_full_df.to_csv(output_dir + "fullresults.csv",sep=",")
    plot_performance(ireceptor_full_df,"iReceptor",output_dir,"IPA#")
    plot_performance(covid_full_df,"COVID19",output_dir,"IPA#")
    plot_performance(external_full_df,"ExternalServices",output_dir,"Service")
