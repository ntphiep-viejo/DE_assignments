from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
import time
import csv
import os

# Configuration for Spark
conf = SparkConf().set("spark.executor.cores", "2")\
                  .set("spark.executor.memory", "2g")

sc = SparkContext(appName="Test", conf=conf)

n_workers = 3  # Number of workers
partition_multiples = range(18, 22, 3)  # Range of partition multiples (3, 6, 9, 12, 15)

from math import sqrt, ceil

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, ceil(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Path to the numbers file and output path
# numbers_file = "/opt/spark/data/numbers.txt"
numbers_file = "/opt/spark/data/numbers_2.txt"
# prime_numbers_rdd_output_path = "/opt/spark/data/results/prime_numbers_rdd.txt"
prime_numbers_rdd_output_path = "/opt/spark/data/results/prime_numbers_rdd_dataset2.txt"
# Path to the CSV file for logging
csv_file_path = "/opt/spark/data/results/execution_statistics_dataset2.csv"

# Check if CSV file exists, if not, write the header
file_exists = os.path.isfile(csv_file_path)
with open(csv_file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Execution Time (s)", "Number of Workers", "Number of Executors", "Number of Partitions", "Executor Cores", "Executor Memory"])

    for num_partitions in partition_multiples:
        # Start the timer
        start_time = time.time()

        # Load the numbers and process them
        numbers_rdd = sc.textFile(numbers_file)
        numbers_rdd = numbers_rdd.repartition(num_partitions)  # Set the number of partitions
        numbers_rdd = numbers_rdd.map(lambda x: int(x))
        prime_numbers_rdd = numbers_rdd.filter(is_prime)
        prime_numbers_rdd.count()

        # End the timer
        end_time = time.time()
        interval = end_time - start_time
        print(f"Execution time with {num_partitions} partitions: {interval} seconds")

        # Check the number of executors
        sc_java = sc._jsc.sc()
        n_executors = len([executor.host() for executor in sc_java.statusTracker().getExecutorInfos()]) - 1

        # Print memory status and executor count
        print(f"Executor count (excluding driver): {n_executors}")

        # Write the statistics to the CSV file
        writer.writerow([interval, n_workers, n_executors, num_partitions, conf.get("spark.executor.cores"), conf.get("spark.executor.memory")])

print(f"Statistics saved to {csv_file_path}")
