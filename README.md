# power-gadget.py

### Introduction

This is a script that parses power logs collected with [Intel Power Gadget](https://software.intel.com/content/www/us/en/develop/articles/intel-power-gadget.html).

The script summarizes power log contents, calculates standard deviations of CPU utilization and CPU frequencies, normalizes the CPU utilization by frequency and outputs the system's total average power consumption.

#### Warning

This script has only been tested when running PowerLog with a resolution of 1000 (i.e. taking one sample per second). Try different resolutions at your own risk.

### Example Usage

```
> /Applications/Intel\ Power\ Gadget/PowerLog -duration 30 -resolution 1000 -file "foo.csv"
...

> python power-gadget.py --power-log-file foo.csv
Parsed power log file: foo.csv
TABLE
  "System Time": [17:09:47:270, 17:09:48:276, 17:09:49:281, 17:09:50:287, 17:09:51:292, 17:09:52:298, ... (26 more values)]
  "RDTSC": [6.99044361899e+13, 6.99073570737e+13, 6.99102764682e+13, 6.99131960937e+13, 6.99161155349e+13, 6.9919035244e+13, ... (26 more values)]
  "Elapsed Time (sec)": [1.005, 2.011, 3.016, 4.022, 5.027, 6.032, ... (26 more values)]
  "CPU Utilization(%)": [1.665, 1.35, 0.83, 0.813, 0.814, 1.153, ... (26 more values)]
  "CPU Frequency_0(MHz)": [2082.0, 1917.0, 2012.0, 1914.0, 2024.0, 2079.0, ... (26 more values)]
  "CPU Min Frequency_0(MHz)": [1200.0, 1200.0, 1200.0, 1200.0, 1200.0, 1200.0, ... (26 more values)]
  "CPU Max Frequency_0(MHz)": [3600.0, 3600.0, 3600.0, 3600.0, 3600.0, 3600.0, ... (26 more values)]
  "CPU Requsted Frequency_0(MHz)": [2309.0, 2109.0, 2193.0, 2142.0, 2224.0, 2397.0, ... (26 more values)]
  "Processor Power_0(Watt)": [2.47, 2.087, 1.789, 1.784, 1.773, 1.936, ... (26 more values)]
  "Cumulative Processor Energy_0(Joules)": [2.483, 4.581, 6.38, 8.174, 9.956, 11.902, ... (26 more values)]
  "Cumulative Processor Energy_0(mWh)": [0.69, 1.273, 1.772, 2.271, 2.766, 3.306, ... (26 more values)]
  "IA Power_0(Watt)": [0.761, 0.552, 0.369, 0.359, 0.352, 0.508, ... (26 more values)]
  "Cumulative IA Energy_0(Joules)": [0.764, 1.32, 1.691, 2.051, 2.406, 2.916, ... (26 more values)]
  "Cumulative IA Energy_0(mWh)": [0.212, 0.367, 0.47, 0.57, 0.668, 0.81, ... (26 more values)]
  "Package Temperature_0(C)": [44.0, 44.0, 44.0, 44.0, 44.0, 44.0, ... (26 more values)]
  "Package Hot_0": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ... (26 more values)]
  "CPU Min Temperature_0(C)": [41.0, 41.0, 41.0, 41.0, 41.0, 40.0, ... (26 more values)]
  "CPU Max Temperature_0(C)": [46.0, 44.0, 44.0, 44.0, 44.0, 45.0, ... (26 more values)]
  "DRAM Power_0(Watt)": [1.228, 1.113, 1.069, 1.069, 1.066, 1.07, ... (26 more values)]
  "Cumulative DRAM Energy_0(Joules)": [1.234, 2.354, 3.428, 4.504, 5.575, 6.651, ... (26 more values)]
  "Cumulative DRAM Energy_0(mWh)": [0.343, 0.654, 0.952, 1.251, 1.549, 1.847, ... (26 more values)]
  "Package Power Limit_0(Watt)": [45.0, 45.0, 45.0, 45.0, 45.0, 45.0, ... (26 more values)]
  "GT Frequency(MHz)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ... (26 more values)]
  "GT Requsted Frequency(MHz)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ... (26 more values)]
SUMMARY
  Total Elapsed Time (sec): 32.128983
  Measured RDTSC Frequency (GHz): 2.904
  Cumulative Package Energy_0 (Joules): 64.581543
  Cumulative Package Energy_0 (mWh): 17.939317
  Average Package Power_0 (Watt): 2.010071
  Cumulative IA Energy_0 (Joules): 17.44751
  Cumulative IA Energy_0 (mWh): 4.84653
  Average Package IA_0 (Watt): 0.543046
  Cumulative DRAM Energy_0 (Joules): 34.945618
  Cumulative DRAM Energy_0 (mWh): 9.707116
  Average Package DRAM_0 (Watt): 1.087666

CPU UTILIZATION AND FREQUENCY OF SAMPLES
    Average CPU Utilization(%): 1.4456875  (std dev: 0.583998471611)
    Average CPU Frequency(MHz): 1861.03125  (std dev: 140.293327616)

NORMALIZED CPU UTILIZATION (AGGREGATED FROM SAMPLES)
            Cycles Utilized(%): 1.424638658
    Average Cycles Utilized(M): 26.512970625
   Average Cycles Available(M): 1861.03125

POWER USAGE (PROCESSOR OR PACKAGE + DRAM)
  Average Total Power Usage(W): 3.097737
```

### Copy to clipboard for pasting into Google Sheets
If you use the `--copy-friendly` argument you get a minimized output separated by tabs, this allows it to be piped into clipboard and pasted into Google Sheets as two columns. For example, on macOS:

```
python power-gadget.py --power-log-file examples/macos-example.csv --copy-friendly | pbcopy
```

Then, if you're making a comparison with other measurements already pasted into a Google Sheet and you only want to paste in the values column, add `--values-only` like so:

```
python power-gadget.py --power-log-file examples/macos-example.csv --copy-friendly --values-only | pbcopy
```

### Q&A

> What's the difference between "Average CPU Utilization(%)" and "Cycles Utilized(%)"?

"Average CPU Utilization(%)" is the average CPU utilization of all samples, not taking CPU frequencies into account. "Cycles Utilized(%)" is the estimated number of cycles utilized out of all possible cycles, i.e. it takes the CPU frequency of each sample into account.

For example, imagine the two following CPU Utilization and CPU Frequency samples:
```
(5%, 1000 MHz)
(10%, 2000 MHz)
```

The "Average CPU Utilization(%)" is (5% + 10%) / 2 = 7.5%.

The "Cycles Utilized(%)" is (5% * 1000 + 10% * 2000) / (1000 + 2000) = 8.33%.

If the CPU frequency is fairly stable during the measurements, these values will be quite similar. But if the CPU frequencies are variable during the test, the "Cycles Utilized(%)" might give a more honest picture of the amount of workload on the system. When comparing multiple measurements "Average Cycles Available(M)" is of interest.

> What are "Average Cycles Available(M)"?

These are the average "CPU Frequency_0(MHz)" of all samples. When sampling once per second, this is an estimate of the amount of CPU cycles per second, i.e. the "effective MHz" of the processor.

### Tips

Before running any measurements close as many applications as possible, these do not only cause additional load on the system but make the measurements less reliable. It is a good idea to make several measurements and pick one where the standard deviations are small. Less standard deviation = more stable measurements.

Even if the standard deviation is small, it is still possible to get outliers. Be careful with this and when in doubt, measure again to make sure your measurements are reproducible.
