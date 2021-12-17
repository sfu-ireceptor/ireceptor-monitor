#!/bin/bash

######### PERFORMANCE TESTING BASH SCRIPT
######### AUTHOR: LAURA GUTIERREZ FUNDERBURK
######### SUPERVISOR: JAMIE SCOTT, FELIX BREDEN, BRIAN CORRIE
######### CREATED ON: July 10
######### LAST MODIFIED ON: Nov 4, 2019
######### This script is to be run periodically to track query performance of ADC API

TIME1=`date +%Y-%m-%d_%H-%M-%S`

echo "Current working directory: `pwd`"
echo "Starting run at: " ${TIME1}


# ---------------------------------------------------------------------

echo "Begin Script"
echo " "

cd /home/ubuntu/ireceptor-monitor/ADC_API_Testing/Scripts/

python3 adc_performance_testing.py '/home/ubuntu/ireceptor-monitor/ADC_API_Testing/ipa1_ipa2_ipa3_ipa4_ipa5_perf/' 'http://covid19-4.ireceptor.org' 'rearrangement' "/home/ubuntu/ireceptor-monitor/ADC_API_Testing/JSON/facets_queries_for_performance_tests/"

python3 adc_performance_testing.py '/home/ubuntu/ireceptor-monitor/ADC_API_Testing/repertoire_performance/' 'http://covid19-4.ireceptor.org' 'repertoire' "/home/ubuntu/ireceptor-monitor/ADC_API_Testing/JSON/repertoire_selected_queries/"

echo "End Script"

