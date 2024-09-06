# malicious-links
This program continuously downloads a list of potentially malicious URLs from a specified source and processes it to categorize IPs and domains. 


It performs the following actions in each iteration:

1. **Downloads the file** from a given URL.
2. **Classifies the data** into IPs and domains.
3. **Updates four files**:
   - `last-ips-list.txt`: Adds only new IPs from the latest iteration.
   - `last-domains-list.txt`: Adds only new domains from the latest iteration.
   - `new-detected-ips-domains-list.txt`: Contains only the newly detected IPs and domains for the current iteration (emptied if none found).
   - `total-malicious-list.txt`: Maintains a cumulative list of all unique IPs and domains across iterations.
4. **Removes the temporary file** used for each download after processing.
5. **Repeats the process** at regular intervals.
