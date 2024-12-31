# Option 1 ##############################################################################################################
# 1. Check
# # netsh interface ipv4 show excludedportrange protocol=tcp

# 2. Exclude
# netsh int ipv4 delete excludedportrange protocol=tcp startport=5141 numberofports=100 # This will remove the entire range of 100 ports from 5141 to 5240.

# 3. Re-add
# netsh int ipv4 add excludedportrange protocol=tcp startport=5141 numberofports=32 # Add the range 5141–5172
# netsh int ipv4 add excludedportrange protocol=tcp startport=5174 numberofports=67 # Add the range 5174–5240

# Option 2 ##############################################################################################################
# net stop winnat
# docker start ...
# net start winnat