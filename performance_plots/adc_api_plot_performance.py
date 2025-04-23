######### PERFORMANCE TESTING PYTHON SCRIPT
######### AUTHOR: LAURA GUTIERREZ FUNDERBURK
######### SUPERVISOR: JAMIE SCOTT, FELIX BREDEN, BRIAN CORRIE
######### CREATED ON: MAY 20, 2019
######### LAST MODIFIED ON: April 29, 2020
"""

Description: this script takes as input a set of .csv files containing performance query results and it outputs a series of plots comparing hourly time taken to finish query
for queries junction_aa, junction_aa_length, v_call (a family, a gene and an allele), d_call (a family, a gene and an allele) and j_call (a family, a gene and an allele) 

"""

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os
import sys
import argparse
import numpy as np
import plotly.io as pio

import plotly.express as px


global all_ipa1,all_ipa2,all_ipa3,all_ipa4,all_ipa5,gold_ipa,all_the_data

def get_mix_col(df):
    fcf = df["filters.content.field"].to_list()
    fcv = df["filters.content.value"].to_list()
    df["filters.content.field:filters.content.value"] = [str(item[0]) + ": " + str(item[1])\
                                                         for item in zip(fcf,fcv)]

    return df


def iterrows_add_value(df):

    generate_values = [eval(row[1]['filters.content'])[0]['content']['value'] for row in df.iterrows()]
    
    return generate_values

def iterrows_add_field(df):

    generate_fields = [eval(row[1]['filters.content'])[0]['content']['field'] for row in df.iterrows()]
    
    return generate_fields

def add_missing_cols(df):
    if 'filters.content.value' not in df.columns:
        df['filters.content.value'] = iterrows_add_value(df)
    if 'filters.content.field' not in df.columns:
        df['filters.content.field'] = iterrows_add_field(df)


def plot_performance(df,name,output_dir):
    try:
        full_fig  = px.line(df,
               y="TimeTaken(s)",
               x="Date/TimeConverted",
               color='filters.content.field:filters.content.value',range_y=[0,500],
           facet_col="Service",title="Time taken per query",hover_name="IPA#",labels={"Date/TimeConverted":"Date","TimeTaken(s)": "Time (s)"})
        # Get rid of facet name (from: https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles)
        full_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        pio.write_html(full_fig,output_dir + str(name) + "_hourly_performance.html",
                  auto_open=True)

        full_fig = px.scatter(df,
               y="RearrangementsPerRepertoire",
               x="Date/TimeConverted",facet_col="Service",title="Number of rearrangements per repertoire",hover_name="IPA#",
               color='filters.content.field:filters.content.value',labels={"Date/TimeConverted":"Date","RearrangementsPerRepertoire": "Average Number of Rearrangements per Repertoire"})
        # Get rid of facet name (from: https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles)
        full_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        pio.write_html(full_fig,output_dir + str(name) + "_rear_per_rep.html",
                  auto_open=True)

        full_fig = px.density_heatmap(df,
               y="RearrangementsPerSecond",
               x="Date/TimeConverted",facet_col="Service",title="Number of rearrangements per second",hover_name="IPA#",labels={"Date/TimeConverted":"Date","RearrangementsPerSecond": "Rearrangements per Second"})
        # Get rid of facet name (from: https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles)
        full_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        pio.write_html(full_fig,output_dir + str(name) + "_HEATMAP_REAR_PER_SEC.html",
                  auto_open=True)

    except:
        print("Warning - missing files for services")


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

    options = getArguments()

    # Get options
    path = options.path
    s_date = options.s_date
    e_date = options.e_date
    output_dir = options.output_dir

    # Get time stamps for start and end.
    date_format = "%Y-%m-%d"
    print("Graphing performance from %s to %s"%(s_date, e_date))
    datetime_object = datetime.datetime.strptime(str(s_date), date_format)
    s_timestamp = datetime_object.timestamp()
    datetime_object = datetime.datetime.strptime(str(e_date), date_format)
    e_timestamp = datetime_object.timestamp()

    # Get the list of files that are within the start and end date.
    files = []
    for item in os.listdir(path):
        file_path = os.path.join(path, item)
        if os.path.isfile(file_path):
            file_timestamp = os.path.getmtime(file_path)
            if file_timestamp >= s_timestamp and file_timestamp <= e_timestamp:
                files.append(file_path)

    all_dfs = []
    for i in range(len(files)):
        try:
            df = pd.read_csv(files[i],sep=',')
        except:
            print("Could not read file %s"%(files[i]))
            continue

        # Add missing columns
        add_missing_cols(df)
        
        # Categorize
        if "ireceptor" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split(".ireceptor.org.csv")[0].split("_")[-1]
        if "vdjserver" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("vdjserver.org.csv")[0].split("_")[-2]
        if "vdjbase" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("airr-seq.vdjbase.org.csv")[0].split("_")[-2]
        if "roche-airr" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("roche-airr.ireceptor.org.csv")[0].split("_")[-2]
        if "scireptor" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("scireptor.dkfz.de.csv")[0].split("_")[-2]
        if "agschwab" in files[i]:
            df["IPA#"] = files[i].split("/")[-1].split("agschwab.uni-muenster.de.csv")[0].split("_")[-2]

        all_dfs.append(df)

    all_the_data = pd.concat([all_dfs[i] for i in range(len(files))],sort=False)

    all_the_data = all_the_data.drop(['Unnamed: 0'], 1)

    # Conver times from str to time stamps (compare when time is off by 1 second)
    all_data_right_times = pd.to_datetime(all_the_data['Date/Time']).dt.floor('T')
    all_the_data["Date/Time"]= all_data_right_times

    all_the_data = all_the_data.sort_values(by=['Date/Time'])

    all_the_data = all_the_data[(all_the_data["Date/Time"] >= pd.Timestamp(str(s_date))) & (all_the_data["Date/Time"] <= pd.Timestamp(str(e_date)))]
    
    
    
    
    all_the_data = get_mix_col(all_the_data)

    allQueries = [item for item in all_the_data.columns if "TIME" in item]
    allQueries2 = [item for item in all_the_data.columns if "SEQUENCES" in item]
    allQueries3 = [item for item in all_the_data.columns if "SAMPLES" in item]

    family_calls = [item for item in allQueries if "f" in item]
    gene_calls = [item for item in allQueries if "g" in item]
    allele_calls = [item for item in allQueries if "a" in item]

    all_the_data["Service"] = ["IPA" + str(item) for item in all_the_data["IPA#"].str.extract('(\d+)')[0]]

    all_ipa1 = all_the_data[(all_the_data["IPA#"]=="ipa1-staging") | (all_the_data["IPA#"]=="ipa1")]
    all_ipa2 = all_the_data[(all_the_data["IPA#"]=="ipa2-staging") | (all_the_data["IPA#"]=="ipa2")]
    all_ipa3 = all_the_data[(all_the_data["IPA#"]=="ipa3-staging") | (all_the_data["IPA#"]=="ipa3")]
    all_ipa4 = all_the_data[(all_the_data["IPA#"]=="ipa4-staging") | (all_the_data["IPA#"]=="ipa4")]
    all_ipa5 = all_the_data[(all_the_data["IPA#"]=="airr-ipa5") | (all_the_data["IPA#"]=="ipa5")]
    all_ipa6 = all_the_data[(all_the_data["IPA#"]=="airr-ipa6") | (all_the_data["IPA#"]=="ipa6")]

    test = pd.concat([all_ipa1,all_ipa2,all_ipa3,all_ipa4,all_ipa5,all_ipa6],sort=False)
    test['RearrangementsPerSecond']=test['NumberRearrangement']/test['TimeTaken(s)']
    test['RearrangementsPerRepertoire']=test['NumberRearrangement']/test['NumberRepertoire']

    plot_performance(test,"ADC_API",output_dir)

    # COVID 19
    all_the_data = all_the_data.drop(["Service"], axis=1)

    covid1 = all_the_data[ (all_the_data["IPA#"]=="covid19-1")]
    covid2 = all_the_data[ (all_the_data["IPA#"]=="covid19-2")]
    covid3 = all_the_data[ (all_the_data["IPA#"]=="covid19-3")]
    covid4 = all_the_data[ (all_the_data["IPA#"]=="covid19-4")]


    covid = pd.concat([covid1,covid2,covid3,covid4],sort=False)

    covid["Service"] = ["COVID19-" + str(covid['IPA#'].to_list()[i].split('-')[1]) for i in range(len(covid['IPA#'].to_list()))]

    covid['RearrangementsPerSecond']=covid['NumberRearrangement']/covid['TimeTaken(s)']
    covid['RearrangementsPerRepertoire']=covid['NumberRearrangement']/covid['NumberRepertoire']
    plot_performance(covid,"COVID19",output_dir)

    # VDJ Server
    print("VDJ Server")
    vdj_df = all_the_data[(all_the_data["IPA#"]=="vdjserver")]
    vdj_df = pd.concat([vdj_df])
    vdj_df['Service'] = ["VDJServer (US)" for i in range(len(vdj_df['IPA#'].to_list()))]
    vdj_df['RearrangementsPerSecond']=vdj_df['NumberRearrangement']/vdj_df['TimeTaken(s)']
    vdj_df['RearrangementsPerRepertoire']=vdj_df['NumberRearrangement']/vdj_df['NumberRepertoire']
    

    # AIRR VDJ Turnkey
    print("AIRR VDJ")
    airr_vdj = all_the_data[(all_the_data["IPA#"]=="airr-seq")]
    airr_vdj = pd.concat([airr_vdj])
    airr_vdj['Service'] = ["VDJBase (Israel)" for i in range(len(airr_vdj['IPA#'].to_list()))]

    # Roche
    print("Roche")
    roche_df = all_the_data[(all_the_data["IPA#"]=="roche-airr")]
    roche_df = pd.concat([roche_df])
    roche_df['Service'] = ["Roche/KCL (Canada)" for i in range(len(roche_df['IPA#'].to_list()))]
    print(roche_df)

    # sciReptor
    print("sciReptor")
    scireptor_df = all_the_data[(all_the_data["IPA#"]=="scireptor")]
    scireptor_df = pd.concat([scireptor_df])
    scireptor_df['Service'] = ["sciReptor (Germany)" for i in range(len(scireptor_df['IPA#'].to_list()))]

    # University of Muenster
    print("Muenster")
    muenster_df = all_the_data[(all_the_data["IPA#"]=="agschwab")]
    muenster_df = pd.concat([muenster_df])
    muenster_df['Service'] = ["Muenster (Germany)" for i in range(len(muenster_df['IPA#'].to_list()))]
    print(muenster_df)

    # Concat DFs together for plotting
    #irec__vdjb_vdjs_df = pd.concat([vdj_df,airr_vdj,irec_df, scireptor_df], ignore_index=True)
    external_df = pd.concat([vdj_df,airr_vdj,scireptor_df,roche_df,muenster_df], ignore_index=True)
    external_df['RearrangementsPerSecond']=external_df['NumberRearrangement']/external_df['TimeTaken(s)']
    external_df['RearrangementsPerRepertoire']=external_df['NumberRearrangement']/external_df['NumberRepertoire']

    # Do the plots
    plot_performance(external_df,"external",output_dir)

