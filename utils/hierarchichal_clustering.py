from scipy.cluster.hierarchy import ward, dendrogram
import matplotlib.pyplot as plt

def hierarchical_cluster (dist,terms,filename):
    linkage_matrix = ward(dist)  #define the linkage_matrix using ward clustering pre-computed distances
    print(linkage_matrix)
    fig, ax = plt.subplots(figsize=(15, 20))  # set size
    ax = dendrogram(linkage_matrix, labels=terms);

    plt.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout()  # show plot with tight layout
    plt.savefig('ward_clusters.png', dpi=600)  # save figure as ward_clusters
