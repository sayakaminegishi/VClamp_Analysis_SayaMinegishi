import matplotlib.pyplot as plt

# Example data
categories = ['Category A', 'Category B', 'Category C', 'Category D']
values = [10, 15, 7, 12]

# Create a line plot
plt.figure(figsize=(10, 6))
plt.plot(categories, values, marker='o')

# Add titles and labels
plt.title('Line Plot with Categorical X-axis')
plt.xlabel('Categories')
plt.ylabel('Values')

# Display the plot
plt.show()