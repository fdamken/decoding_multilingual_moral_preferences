Documentation for generating plot in Figure 3 and related SI figures.

For Python, we require Numpy, Scipy, Scikit-Learn, Pandas, Matplotlib, and Seaborn.  These dependencies can be installed via Anaconda distribution of Python.

0- File RobotoCondensed-Regular.ttf
font-family of Roboto Condensed used in label generation


1- For generating Radial Plots for three cluster, execute the following command in the current directory,

  $ python3 figure3b.py

This will generate an image "radar_plot.pdf" in the image folder.



2- For Radial Dendrogram, start by launching a http server using Python:

	$python3 -m http.server

Open up a browser (preferably, Firefox) and enter http://localhost:8000/culture.html for the url address. This creates SVG image of the radial dendrogram.  Right click anywhere on the image and select "Inspect Element".  Select the svg element, and again, right click to choose "Screenshot Node."  This will save PNG image.


Extended Data Figure 5
———————————————————————
Execute

	$ python3 EDfig5ab.py

generates 'calinski-harabasz.pdf' and 'silhouette.pdf'.


Execute

	$ python3 EDfig5cd.py

generates 'purity.pdf' and 'max-matching.pdf'.


SI figure S8
————————————
S8. Execute

	$ python3 figure_S8.py

generates 'joyplot.pdf'.

SI figure S9
————————————
S9. Execute

	$ python3 figure_S9.py

generates 'distance_matrix.pdf' and 'pca.pdf'.
