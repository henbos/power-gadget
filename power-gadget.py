import sys
import math

# Parsing Power Logs

# Returns (table_keys, table, summaries), where...
# - table_keys is in array of keys in the order that they were parsed.
# - table is a dictionary mapping keys to arrays of all values.
# - summaries is an array of (string, float).
def parse_power_log(filename):
  with open(filename) as file:
    table_keys = []
    table = {}
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
        summaries[key] = value
    return (table_keys, table, summaries)

# E.g. '"item 1","    12.3"' => ["item 1", 12.3]
def parse_items(line):
  # Parse items as strings.
  items = []
  i = line.find('"')
  assert i == 0
  while True:
    i = i + 1
    end = line.find('"', i)
    assert end != -1
    items.append(line[i:end])
    i = end + 1
    if i == len(line):
      break
    assert line[i] == ","
    i = i + 1
  # Remove trailing spaces and convert string-numbers to numbers.
  for i in range(len(items)):
    items[i] = items[i].strip()
    try:
      items[i] = float(items[i])
    except ValueError:
      pass
  return items

def print_parsed_power_log(table_keys, table, summaries):
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
  for key in summaries:
    print("  {0}: {1}".format(key, summaries[key]))

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

def main():
  try:
    arguments = parse_argv()
  except AssertionError:
    print("Error parsing command line arguments.")
    print("")
    arguments = {"--help": ""}
  if "--help" in arguments:
    print("Example Usage:")
    print("  python power-gadget.py --power-log-file 'test.pl'")
    return
  if "--power-log-file" in arguments:
    power_log_filename = arguments.pop("--power-log-file")
    if len(power_log_filename) == 0:
      print("--power-log-file has to specify a filename")
      return
  else:
    print("Missing mandatory argument: --power-log-file")
    return
  if len(arguments) > 0:
    line = "Unrecognized arguments:"
    for key in arguments:
      line += " " + key
    print(line)
    return

  kCpuUtilizationKey = "CPU Utilization(%)"
  kCpuFrequencyKey = "CPU Frequency_0(MHz)"
  kAveragePackagePowerKey = "Average Package Power_0 (Watt)"
  kAverageDramPowerKey = "Average Package DRAM_0 (Watt)"

  # Parse Power Log
  (table_keys, table, summaries) = parse_power_log(power_log_filename)
  print("Parsed power log file: " + power_log_filename)
  print_parsed_power_log(table_keys, table, summaries)
  print("")

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
  # There are three average powers listed in PowerLog's summary: package, IA and
  # DRAM. IA is supposedly a subset of the package, so the total is said to be
  # package + DRAWM.
  average_power_usage = summaries[kAveragePackagePowerKey] +\
                        summaries[kAverageDramPowerKey]

  # Results
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
  print("POWER USAGE (PACKAGE + DRAM)")
  print("  Average Total Power Usage(W): {0}".format(average_power_usage))

if __name__ == "__main__":
  main()
