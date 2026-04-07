import matplotlib.pyplot as plt
# 1st graph function is Accuracy vs Satellites graph while
# 2nd graph function is Collections vs Satellites graph

def graph(total_accuracies1, total_accuracies2, no_of_sats, no_of_stations, time_horizon, no_of_regions):
    """
    Plots two accuracy arrays against the number of satellites and 
    displays simulation parameters on the graph.
    """
    # 1. Create the canvas
    plt.figure(figsize=(8, 6))

    # 2. Plot the two lines
    # marker='o' adds dots, linestyle='-' joins them with a solid line
    plt.plot(no_of_sats, total_accuracies1, marker='o', linestyle='-', color='blue', label='ILP-1: Model with battery constraints')
    
    # marker='s' adds squares, linestyle='--' joins them with a dashed line
    plt.plot(no_of_sats, total_accuracies2, marker='s', linestyle='--', color='red', label='ILP-2: Model without battery constraints')

    # 3. Add Titles and Axis Labels
    # plt.title('System Accuracy vs. Number of Satellites', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Satellites', fontsize=22)
    plt.ylabel('Collection Performance (%)', fontsize=22)

    # Force the X-axis to only display whole numbers
    plt.xticks(no_of_sats, fontsize=22)
    plt.yticks(fontsize=22)

    # 4. Create the Parameter Text Box
    # \n creates a new line for each parameter
    param_text = (
        f"Simulation Parameters:\n"
        f"• Stations: {no_of_stations}\n"
        f"• Regions: {no_of_regions}\n"
        f"• Time Horizon: {time_horizon}"
    )
    
    # Add the text box to the plot
    # x=0.05, y=0.95 anchors it to the top-left corner. 
    # bbox creates a white background so the grid lines don't run through the text.
    plt.gca().text(
        0.05, 0.9, param_text, 
        transform=plt.gca().transAxes, 
        fontsize=20,
        verticalalignment='top', 
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9)
    )

    # 5. Add Grid and Legend
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc='lower right', fontsize=15.5,bbox_to_anchor=(1, -0.016)) # You can change to 'upper right' if it overlaps data

    # 6. Save as PDF for Overleaf
    filename = 'accuracy_vs_satellites.pdf'
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    print(f"[Plotting] Graph saved successfully as '{filename}'")

    # 7. Clear the canvas so future function calls don't draw on top of this one
    plt.clf()
    plt.close()

def graph_for_collections(total_validated_collections, total_expected_collections, no_of_sats, no_of_stations, time_horizon, no_of_regions):
    """
    Plots two accuracy arrays against the number of satellites and 
    displays simulation parameters on the graph.
    """
    # 1. Create the canvas
    plt.figure(figsize=(8, 6))

    # 2. Plot the two lines
    # marker='o' adds dots, linestyle='-' joins them with a solid line
    plt.plot(no_of_sats, total_validated_collections, marker='o', linestyle='-', color='blue', label='ILP-1: Model with battery constraints')
    
    # marker='s' adds squares, linestyle='--' joins them with a dashed line
    plt.plot(no_of_sats, total_expected_collections, marker='s', linestyle='--', color='red', label='ILP-2: Model without battery constraints')

    # 3. Add Titles and Axis Labels
    # plt.title('System Accuracy vs. Number of Satellites', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Satellites', fontsize=22)
    plt.ylabel('No of Collections', fontsize=22)

    # Force the X-axis to only display whole numbers
    plt.xticks(no_of_sats, fontsize=22)
    plt.yticks(fontsize=22)

    # 4. Create the Parameter Text Box
    # \n creates a new line for each parameter
    param_text = (
        f"Simulation Parameters:\n"
        f"• Stations: {no_of_stations}\n"
        f"• Regions: {no_of_regions}\n"
        f"• Time Horizon: {time_horizon}"
    )
    
    # Add the text box to the plot
    # x=0.05, y=0.95 anchors it to the top-left corner. 
    # bbox creates a white background so the grid lines don't run through the text.
    plt.gca().text(
        0.61, 0.47, param_text, 
        transform=plt.gca().transAxes, 
        fontsize=20,
        verticalalignment='top', 
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.6)
    )

    # 5. Add Grid and Legend
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc='lower right', fontsize=15.5,bbox_to_anchor=(1, -0.016)) # You can change to 'upper right' if it overlaps data

    # 6. Save as PDF for Overleaf
    filename = 'collections_vs_satellites.pdf'
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    print(f"[Plotting] Graph saved successfully as '{filename}'")

    # 7. Clear the canvas so future function calls don't draw on top of this one
    plt.clf()
    plt.close()

# --- Example of how you would call this function ---
if __name__ == "__main__":
    sats = [1, 2, 3, 4, 5]
    acc1 = [55.5, 68.2, 75.0, 82.1, 89.4]
    acc2 = [60.0, 72.1, 80.5, 88.0, 94.2]
    
    graph(
        total_accuracies1=acc1, 
        total_accuracies2=acc2, 
        no_of_sats=sats, 
        no_of_stations=4, 
        time_horizon=675, 
        no_of_regions=12
    )