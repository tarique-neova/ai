import matplotlib.pyplot as plt

# Data
labels_functionality = ['Scan', 'Scan and Save', 'Save']
sizes_functionality = [8, 4, 5]
colors_functionality = ['lightblue', 'lightgreen', 'lightcoral']
explode_functionality = (0.1, 0, 0)  # explode the first slice

labels_status = ['Success', 'Not Applicable']
sizes_status = [15, 3]
colors_status = ['gold', 'silver']
explode_status = (0, 0.1)  # explode the second slice

# Plotting for Functionality
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.pie(sizes_functionality, explode=explode_functionality, labels=labels_functionality,
        colors=colors_functionality, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title("Functionality Distribution")

# Plotting for File Save Status
plt.subplot(1, 2, 2)
plt.pie(sizes_status, explode=explode_status, labels=labels_status,
        colors=colors_status, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title("File Save Status")

plt.tight_layout()
plt.show()
