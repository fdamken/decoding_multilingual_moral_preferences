# Experiment Results
This directory contains results from experiments. The results are organized
according to their stage in the result processing pipeline. See below for more
detailed information on which directories contain what.

## `raw`
This directory contains results as they were produced by the experiments with no
further processing. In particular, results may be incomplete, contain unexpected
data, or be otherwise unpolished.

## `cleansed`
This directory contains cleansed results. Note that these are not further
preprocessed or analyzed, but they have been cleaned up to remove unexpected
data, fill in missing data, and otherwise make the results easier to work with.

In particular, some of the `raw` results contain errors due to API problems and
similar issues.

Note that, as these results are composed of multiple experiment runs, the meta
information is invalid. For detailed meta information, see the `raw` results.
Note that it can be very cumbersome to associate the cleansed results with the
metadata, but this is also not really necessary.

In an updated version of the experiment code, failed games are automatically
retried and the step of manual data imputation became unnecessary. However, to
avoid repeated experiments, we decided to keep the imputed data as the retry
approach did not majorly change the experiment setup and results are still
comparable. But things are easier now.

## `preprocessed`
This directory contains preprocessed results. That is, CSV files extracted from
the JSON format of the cleansed results. These also link every played scenario
to a scenario ID to be used for analysis.
