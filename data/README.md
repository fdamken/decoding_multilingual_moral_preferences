# Data
This directory contains the data used for querying the models.
Subdirectory `raw` contains the raw data (generated using the process described below).
Subdirectory `preprocessed` contains the preprocessed data that is actually used for querying.

**Note that the exact data used in the experiments is included in this repository, and it is not necessary to perform these steps.**

**Also note that the order of the scenarios is _extremely_ important and the dataset shall not be randomized! Each consecutive 13 scenarios have to be faced in one game.**


## Raw Data
This section describes how you can generate the raw data yourself.
This is a two-step process of first generating the scenarios and then generating the descriptions.

### Scenario Generation
On the MoralMachine's website, click on “Judge” and then paste the following snippet into the console.
This will generate 13 scenarios per iteration (i.e., 13000 scenarios overall) and save them in the `scenarios` array.

```javascript
const num_samples = 13000;
const scenarios = [];
for (let i = 0; i < num_samples / 13; i++) {
    scenarios.push(...Helpers.generateScenarios());
}
```

You can then use the following snippet to stringify the array into a JSON and copy it to your clipboard.

```javascript
setTimeout(() => navigator.clipboard.writeText(JSON.stringify(scenarios)), 1000);
```

Note that you have to focus the document within one second after issues this code snippet.

You should get a similar result to the data in `scenarios.json`.


### Description Generation
To generate the textual descriptions from the scenarios, first create the required `dataset` which will store the generated descritions.

```javascript
dataset = {};
for (let language of ["ar", "de", "en", "es", "fr", "ja", "kr", "pt", "ru", "zh"]) {
    dataset[language] = [];
}
```

Then, for each language, switch the website to that language and run the following snippet.

```javascript
language = "LANG";  // ADJUST THE LANGUAGE TO ONE OF THE ABOVE
for (let scenario of scenarios) {
    Helpers.makeDescription(scenario);
    dataset[language].push([Session.get("leftcontent"), Session.get("rightcontent")]);
}
```

Finally, stringify the dataset and copy it to your clipboard.

```javascript
setTimeout(() => navigator.clipboard.writeText(JSON.stringify(dataset[language])), 1000)
```

Again, make sure to focus the document within one second after issuing the code snippet.

You should get a similar result to the data in `dataset_LANG.json`.


## Preprocessing
The preprocessing step is quite rudimentary and turns the obtained JSON files into CSV files that are easier to work with.
Simply run the script `preprocessed/preprocess.py`.
