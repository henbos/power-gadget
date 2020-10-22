import sys
import math

# Parsing Power Logs

# Returns (table_keys, table, summaries), where...
# - table_keys is in array of table keys in the parsing order.
# - table is a dictionary mapping keys to arrays of all values.
# - summaries_keys is an array of summaries keys in the parsing order.
# - summaries is an array of (string, float).
def parse_power_log(filename):
  with open(filename) as file:
    table_keys = []
    table = {}
    summaries_keys = []
    summaries = {}

    is_parsing_table = True
    # Parse file.
    for line in file:
      # Remove trailing spaces, including end-of-line characters.
      line = line.strip()
      if len(line) == 0:
        is_parsing_table = False
        continue
      items = parse_items(line)
      if is_parsing_table:
        # Table parsing logic.
        if len(table_keys) == 0:
          table_keys = items
          for key in table_keys:
            table[key] = []
        else:
          assert len(items) == len(table_keys)
          for i in range(len(items)):
            key = table_keys[i]
            table[key].append(items[i])
      else:
        # Summaries parsing logic.
        assert len(items) == 1
        i = items[0].find(" = ")
        assert i != -1
        key = items[0][:i]
        value = items[0][i + 3:]
        value = float(value)
        summaries_keys.append(key)
        summaries[key] = value
    return (table_keys, table, summaries_keys, summaries)

# On macOS items are enclosed by quotes. On Windows, they are not.
# macOS example: '"item 1","    12.3"' => ["item 1", 12.3]
# Windows example: 'item 1,    12.3' => ["item 1", 12.3]
def parse_items(line):
  # Parse items as strings.
  items = []
  i = line.find('"')
  if i == 0:
    # macOS parsing.
    while True:
      i += 1
      end = line.find('"', i)
      assert end != -1
      items.append(line[i:end])
      i = end + 1
      if i == len(line):
        break
      assert line[i] == ","
      i += 1
  else:
    # Windows parsing.
    while True:
      i += 1
      end = line.find(',', i)
      if end == -1:
        end = len(line)
      items.append(line[i:end])
      i = end
      if i == len(line):
        break
      assert line[i] == ","
  # Remove trailing spaces and convert string-numbers to numbers.
  for i in range(len(items)):
    items[i] = items[i].strip()
    try:
      items[i] = float(items[i])
    except ValueError:
      pass
  return items

def print_parsed_power_log(table_keys, table, summaries_keys, summaries):
  print("TABLE")
  for key in table_keys:
    line = '  "' + key + '": ['
    values = table[key]
    i = 0
    for value in values:
      if i != 0:
        line += ", "
      if i == 6:
        line += "... (" + str(len(values) - i) + " more values)"
        break
      line += str(value)
      i = i + 1
    line += "]"
    print(line)
  print("SUMMARY")
  for key in summaries_keys:
    print("  {0}: {1}".format(key, summaries[key]))

# Math utils

def calculate_standard_deviation(values):
  mean = 0
  for value in values:
    mean = mean + value
  mean = mean / len(values)
  # The variance is the average of the squared differences from the mean.
  variance = 0
  for value in values:
    sample = value - mean
    sample = sample * sample
    variance += sample
  variance = variance / len(values)
  # The standard deviation is the squaree root of the variance.
  standard_deviation = math.sqrt(variance)
  return (standard_deviation, variance, mean)

# Main

def parse_argv():
  arguments = {}
  i = 1
  while i < len(sys.argv):
    key = sys.argv[i]
    assert key.startswith("--")
    assert key.find("=") == -1
    value = ""
    if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
      i = i + 1
      value = sys.argv[i]
    arguments[key] = value
    i = i + 1
  return arguments

def main():
  try:
    arguments = parse_argv()
  except AssertionError:
    print("Error parsing command line arguments.")
    print("")
    arguments = {"--help": ""}
  if "--help" in arguments:
    print("Use --power-log-file to specify the log file.")
    print("Optionally, use --copy-friendly for a shorter copy-friendly result.")
    print("")
    print("Example Usage:")
    print("  python power-gadget.py --power-log-file 'test.csv'")
    print("")
    print("Copying to clipboard on macOS to be pasted into a Google Sheet:")
    print("  python power-gadget.py --power-log-file examples/macos-example.csv"
          " --copy-friendly | pbcopy")
    return
  if "--power-log-file" in arguments:
    power_log_filename = arguments.pop("--power-log-file")
    if len(power_log_filename) == 0:
      print("--power-log-file has to specify a filename")
      return
  else:
    print("Missing mandatory argument: --power-log-file")
    return
  copy_friendly = arguments.pop("--copy-friendly", None) != None
  if len(arguments) > 0:
    line = "Unrecognized arguments:"
    for key in arguments:
      line += " " + key
    print(line)
    return

  # Parse Power Log
  (table_keys, table, summaries_keys, summaries) =\
      parse_power_log(power_log_filename)

  kCpuUtilizationKey = "CPU Utilization(%)"
  kCpuFrequencyKey = "CPU Frequency_0(MHz)"
  cpu_utilization_values = table[kCpuUtilizationKey]
  cpu_frequency_values = table[kCpuFrequencyKey]
  assert len(cpu_utilization_values) == len(cpu_frequency_values)

  # Average CPU Utilization
  (cpu_utilization_std_dev, cpu_utilization_var, cpu_utilization_mean) =\
      calculate_standard_deviation(cpu_utilization_values)

  # Average CPU Frequency
  (cpu_frequency_std_dev, cpu_frequency_var, cpu_frequency_mean) =\
      calculate_standard_deviation(cpu_frequency_values)

  # CPU Utilization Normalized by Frequency
  total_cycles_utilized = 0
  total_cycles_available = 0
  for i in range(len(cpu_utilization_values)):
    total_cycles_utilized +=\
        cpu_utilization_values[i] * 0.01 * cpu_frequency_values[i]
    total_cycles_available += cpu_frequency_values[i]
  cycles_utilized_percentage =\
      (total_cycles_utilized / total_cycles_available) * 100
  cycles_utilized_per_sample =\
      total_cycles_utilized / len(cpu_utilization_values)
  cycles_available_per_sample =\
      total_cycles_available / len(cpu_utilization_values)

  # Power Usage
  #
  # On Windows, there are four average powers listed in PowerLog's summary:
  # processor, IA, DRAM and GT. Per documentation[1], the processor power is a
  # summary of IA, GT and others not measured. As such, the total power of the
  # system is estimated as "processor + DRAM".
  #
  # On macOS, there are three average powers:
  # package, IA and DRAM. Assuming package also includes the IA, the total power
  # of the system is estimated as "package + DRAM".
  #
  # [1] https://software.intel.com/content/www/us/en/develop/articles/intel-power-gadget.html
  kAverageProcessorPowerKey = "Average Processor Power_0 (Watt)"  # Windows
  kAverageDramPowerKey = "Average DRAM Power_0 (Watt)"            # Windows
  kAveragePackagePowerKey = "Average Package Power_0 (Watt)"      # macOS
  kAveragePackageDramPowerKey = "Average Package DRAM_0 (Watt)"   # macOS
  average_power_usage = summaries.get(kAverageProcessorPowerKey, 0) +\
                        summaries.get(kAverageDramPowerKey, 0) +\
                        summaries.get(kAveragePackagePowerKey, 0) +\
                        summaries.get(kAveragePackageDramPowerKey, 0)

  # Print results
  if not copy_friendly:
    print("Parsed power log file: " + power_log_filename)
    print_parsed_power_log(table_keys, table, summaries_keys, summaries)
    print("")
    print("CPU UTILIZATION AND FREQUENCY OF SAMPLES")
    print("    Average CPU Utilization(%): {0}  (std dev: {1})".format(\
              cpu_utilization_mean, cpu_utilization_std_dev))
    print("    Average CPU Frequency(MHz): {0}  (std dev: {1})".format(\
              cpu_frequency_mean, cpu_frequency_std_dev))
    print("")
    print("NORMALIZED CPU UTILIZATION (AGGREGATED FROM SAMPLES)")
    print("            Cycles Utilized(%): {0}".format(\
              cycles_utilized_percentage))
    print("    Average Cycles Utilized(M): {0}".format(\
              cycles_utilized_per_sample))
    print("   Average Cycles Available(M): {0}".format(\
              cycles_available_per_sample))
    print("")
    print("POWER USAGE (PROCESSOR OR PACKAGE + DRAM)")
    print("  Average Total Power Usage(W): {0}".format(average_power_usage))
  else:
    for key in summaries_keys:
      print("{0}\t{1}".format(key, summaries[key]))
    print("\t")
    print("Average CPU Utilization(%)\t{0}".format(cpu_utilization_mean))
    print("Average CPU Utilization(%) std dev\t{0}".format(\
          cpu_utilization_std_dev))
    print("Average CPU Frequency(MHz)\t{0}".format(cpu_frequency_mean))
    print("Average CPU Frequency(MHz) std dev\t{0}".format(\
          cpu_frequency_std_dev))
    print("\t")
    print("Cycles Utilized(%)\t{0}".format(cycles_utilized_percentage))
    print("Average Cycles Utilized(M)\t{0}".format(cycles_utilized_per_sample))
    print("Average Cycles Available(M)\t{0}".format(\
          cycles_available_per_sample))
    print("\t")
    print("Average Total Power Usage(W)\t{0}".format(average_power_usage))

if __name__ == "__main__":
  main()
