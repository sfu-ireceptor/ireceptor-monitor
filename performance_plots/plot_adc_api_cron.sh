
#!/bin/bash

SCRIPT_DIR=`dirname "$0"`

EDATE=$(date "+%Y-%m-%d" -d "2 days")
SDATE=$(date "+%Y-%m-%d" -d "30 days ago")
DATE=$(date)
echo ${DATE}

echo "Running from ${SCRIPT_DIR}"

# Pull the ADC API plot github repo. We do this in the home directory.
echo "Pulling repo"

cd /home/ubuntu/ADC-API-Plots/
git pull https://github.com/sfu-ireceptor/ADC-API-Plots

# Remove all of the rearrangement plots (ADC API, COVID, External)
# We overwrite these each time.
echo "Cleaning repo"
cd ADC-API-Plots/rearrangement/
for x in ADC_API*;do rm "$x";done
for x in COVID19*;do rm "$x";done
for x in external*;do rm "$x";done
cd ..

# Remove all of the repertoire plots
cd ./repertoire/
for x in *.html;do rm "$x";done
cd ..

# Generate the new performance plots for rearrangements
echo "Performance test results (rearrangement)"
python3 ${SCRIPT_DIR}/adc_api_plot_performance.py /home/ubuntu/performance/rearrangement/ ${SDATE} ${EDATE} "./rearrangement/"

# Generate the new performance plots for repertoires
echo "Performance test results (repertoire)"
python3 ${SCRIPT_DIR}/plot_repertoire_performance.py /home/ubuntu/performance/repertoire/ ${SDATE} ${EDATE} "./repertoire/"

# Add the new plots to the github branch, commit, and push.
git add .
git commit -m "add plot from "${SDATE}" to "${EDATE}
git push origin master


