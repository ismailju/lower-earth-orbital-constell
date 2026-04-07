import matplotlib.pyplot as plt

def graph(total_accuracies1, total_accuracies2, stationsOnlyList, regionsOnly, time_horizon, satsOnly):
    """
    Plots two accuracy arrays against the number of satellites and 
    displays simulation parameters on the graph.
    """
    # 1. Create the canvas
    plt.figure(figsize=(8, 6))

    # 2. Plot the two lines
    # marker='o' adds dots, linestyle='-' joins them with a solid line
    plt.plot(stationsOnlyList, total_accuracies1, marker='o', linestyle='-', color='blue', label='ILP-1: Model with battery constraints')
    
    # marker='s' adds squares, linestyle='--' joins them with a dashed line
    plt.plot(stationsOnlyList, total_accuracies2, marker='s', linestyle='--', color='red', label='ILP-2: Model without battery constraints')

    # 3. Add Titles and Axis Labels
    # plt.title('System Accuracy vs. Number of Regions', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Stations', fontsize=22)
    plt.ylabel('Collection Performance (%)', fontsize=22)

    # Force the X-axis to only display whole numbers
    plt.xticks(stationsOnlyList,fontsize=22)
    plt.yticks(fontsize=22)

    # 4. Create the Parameter Text Box
    # \n creates a new line for each parameter
    param_text = (
        f"Simulation Parameters:\n"
        f"• Regions: {regionsOnly}\n"
        f"• Satellites: {satsOnly}\n"
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
    plt.legend(loc='lower right',fontsize=16, bbox_to_anchor=(0.90, 0.3)) # You can change to 'upper right' if it overlaps data

    # 6. Save as PDF for Overleaf
    filename = 'accuracy_vs_stations.pdf'
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    print(f"[Plotting] Graph saved successfully as '{filename}'")

    # 7. Clear the canvas so future function calls don't draw on top of this one
    plt.clf()
    plt.close()

def graph_for_collections(total_validated_collections, total_expected_collections, stationsOnlyList, regionsOnly, time_horizon, satsOnly):
    """
    Plots two accuracy arrays against the number of satellites and 
    displays simulation parameters on the graph.
    """
    # 1. Create the canvas
    plt.figure(figsize=(8, 6))

    # 2. Plot the two lines
    # marker='o' adds dots, linestyle='-' joins them with a solid line
    plt.plot(stationsOnlyList, total_validated_collections, marker='o', linestyle='-', color='blue', label='ILP-1: Model with battery constraints')
    
    # marker='s' adds squares, linestyle='--' joins them with a dashed line
    plt.plot(stationsOnlyList, total_expected_collections, marker='s', linestyle='--', color='red', label='ILP-2: Model without battery constraints')

    # 3. Add Titles and Axis Labels
    # plt.title('System Accuracy vs. Number of Regions', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Stations', fontsize=22)
    plt.ylabel('No of Collections', fontsize=22)

    # Force the X-axis to only display whole numbers
    plt.xticks(stationsOnlyList,fontsize=22)
    plt.yticks(fontsize=22)

    # 4. Create the Parameter Text Box
    # \n creates a new line for each parameter
    param_text = (
        f"Simulation Parameters:\n"
        f"• Regions: {regionsOnly}\n"
        f"• Satellites: {satsOnly}\n"
        f"• Time Horizon: {time_horizon}"
    )
    
    # Add the text box to the plot
    # x=0.05, y=0.95 anchors it to the top-left corner. 
    # bbox creates a white background so the grid lines don't run through the text.
    plt.gca().text(
        0.05, 0.8, param_text, 
        transform=plt.gca().transAxes, 
        fontsize=20,
        verticalalignment='top', 
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9)
    )

    # 5. Add Grid and Legend
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc='lower right',fontsize=16, bbox_to_anchor=(0.90, 0.3)) # You can change to 'upper right' if it overlaps data

    # 6. Save as PDF for Overleaf
    filename = 'collections_vs_stations.pdf'
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    print(f"[Plotting] Graph saved successfully as '{filename}'")

    # 7. Clear the canvas so future function calls don't draw on top of this one
    plt.clf()
    plt.close()