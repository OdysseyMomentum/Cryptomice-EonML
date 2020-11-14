# Cryptomice-EonML
Cryptomice-EonML is the Machine Learning module for the
Odyssey Momentum hackathon.

## How to install
Cryptomice-EonML requires Python3 and Virtualenv installed, execute the script `build.sh` in order to download requirements and set up the environment.

## How to use

### Create a new model
Create a dataset in a file called `training.json` with all trainings informations.

```
{
  "append": false,
  "dataset":[
    {"result": 1, "data": "1,1,0,0.2,0"},
    {"result": 1, "data": "0,0,1,0.1,1"},
    {"result": 0, "data": "0,1,0,0.4,0"},
    {"result": 0, "data": "0,0,1,0.3,0"},
    {"result": 0, "data": "0,0,1,0.2,0"},
    {"result": 1, "data": "1,0,1,0.4,0"},
    {"result": 0, "data": "0,0,1,0.1,0"},
    {"result": 0, "data": "0,0,1,0.2,0"},
    {"result": 1, "data": "0,0,1,0.1,1"},
    {"result": 1, "data": "1,1,0,0.3,0"},
    {"result": 1, "data": "1,0,0,0.4,1"},
    {"result": 0, "data": "0,1,1,0.5,0"}
  ]
}
```

Call the `/model/<model>/train` API where <model> is the name of your model.

```
curl http://localhost:5005/model/supplychain123/train -d @training.json -H 'Content-Type: application/json' | jq

{
  "results": [
    "SVM-light Version V6.02",
    "0 # kernel type",
    "3 # kernel parameter -d",
    "1 # kernel parameter -g",
    "1 # kernel parameter -s",
    "1 # kernel parameter -r",
    "empty# kernel parameter -u",
    "5 # highest feature index",
    "24 # number of training documents",
    "12 # number of support vectors plus 1",
    "-0.11942091 # threshold b, each following line is a SV (starting with alpha*y)",
    "-0.4684569126832371921409503556788 1:0 2:0 3:1 4:0.2 5:0 #",
    "0.14717487910546045437598650096334 1:1 2:1 3:0 4:0.2 5:0 #",
    "-0.16659578405527497579896589741111 1:0 2:1 3:0 4:0.40000001 5:0 #",
    "-0.53629968728469634697830770164728 1:0 2:1 3:1 4:0.5 5:0 #",
    "0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:1 #",
    "-0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:0 #",
    "0.61398330903942865965916553250281 1:1 2:1 3:0 4:0.30000001 5:0 #",
    "-0.61398330903942865965916553250281 1:1 2:0 3:0 4:0.40000001 5:1 #",
    "0.61398330903942865965916553250281 1:1 2:0 3:1 4:0.40000001 5:0 #",
    "0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:1 #",
    "-0.20378911316110831508652267984871 1:0 2:0 3:1 4:0.2 5:0 #"
  ],
  "status": [
    "Scanning examples...done",
    "Reading examples into memory...OK. (12 examples read)",
    "Setting default regularization parameter C=0.6140",
    "Optimizing..............done. (15 iterations)",
    "Optimization finished (maxdiff=0.00000).",
    "Runtime in cpu-seconds: 0.00",
    "Number of SV: 11 (including 6 at upper bound)",
    "L1 loss: loss=0.76660",
    "Norm of weight vector: |w|=0.99891",
    "Norm of longest example vector: |x|=1.50000",
    "Number of kernel evaluations: 386",
    "Writing model file...done"
  ]
}
```

### Get a prediction
Create a dataset in a file called `dataset.json` with all information for requested predictions.

```
{
  "dataset":[
    {"data": "1,0,0,0.2,1"},
    {"data": "1,1,0,0.3,0"},
    {"data": "0,0,0,0.2,1"},
    {"data": "1,0,1,0.2,0"}
  ]
}
```

Call the `/model/<model>/predict` API where <model> is the name of your model.

```
curl http://localhost:5005/model/supplychain123/predict -d @dataset.json -H 'Content-Type: application/json' | jq

{
  "results": [
    {
      "data": "1 1:1 2:0 3:0 4:0.2 5:1",
      "result": "1.4557206"
    },
    {
      "data": "2 1:1 2:1 3:0 4:0.3 5:0",
      "result": "0.8805791"
    },
    {
      "data": "3 1:0 2:0 3:0 4:0.2 5:1",
      "result": "0.69456241"
    },
    {
      "data": "4 1:1 2:0 3:1 4:0.2 5:0",
      "result": "0.86115819"
    }
  ],
  "status": [
    "Reading model...OK. (11 support vectors read)",
    "Classifying test examples..done",
    "Runtime (without IO) in cpu-seconds: 0.00"
  ]
}
```


If you want call the service using a simple GET call you can encode your request directly in the url (maximum 1 request).

```
http://localhost:5005/model/supplychain123/predict?data=1,0,1,0.2,0

{
  "results": [
    "0.86115819"
  ]
}
```

### Update the model
Create a dataset in a file called `training.json` with new trainings informations, and set append to true.

```
{
  "append": true,
  "dataset":[
    {"result": 1, "data": "1,1,0,0.2,0"},
    {"result": 1, "data": "0,0,1,0.1,1"},
    {"result": 0, "data": "0,1,0,0.4,0"},
    {"result": 0, "data": "0,0,1,0.3,0"},
    {"result": 0, "data": "0,0,1,0.2,0"},
    {"result": 1, "data": "1,0,1,0.4,0"}
  ]
}
```
Call the `/model/<model>/train` API where <model> is the name of the model you want update.

```
curl http://localhost:5005/model/supplychain123/train -d @training.json -H 'Content-Type: application/json' | jq

{
  "results": [
    "SVM-light Version V6.02",
    "0 # kernel type",
    "3 # kernel parameter -d",
    "1 # kernel parameter -g",
    "1 # kernel parameter -s",
    "1 # kernel parameter -r",
    "empty# kernel parameter -u",
    "5 # highest feature index",
    "24 # number of training documents",
    "12 # number of support vectors plus 1",
    "-0.11942091 # threshold b, each following line is a SV (starting with alpha*y)",
    "-0.4684569126832371921409503556788 1:0 2:0 3:1 4:0.2 5:0 #",
    "0.14717487910546045437598650096334 1:1 2:1 3:0 4:0.2 5:0 #",
    "-0.16659578405527497579896589741111 1:0 2:1 3:0 4:0.40000001 5:0 #",
    "-0.53629968728469634697830770164728 1:0 2:1 3:1 4:0.5 5:0 #",
    "0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:1 #",
    "-0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:0 #",
    "0.61398330903942865965916553250281 1:1 2:1 3:0 4:0.30000001 5:0 #",
    "-0.61398330903942865965916553250281 1:1 2:0 3:0 4:0.40000001 5:1 #",
    "0.61398330903942865965916553250281 1:1 2:0 3:1 4:0.40000001 5:0 #",
    "0.61398330903942865965916553250281 1:0 2:0 3:1 4:0.1 5:1 #",
    "-0.20378911316110831508652267984871 1:0 2:0 3:1 4:0.2 5:0 #"
  ],
  "status": [
    "Scanning examples...done",
    "Reading examples into memory...OK. (12 examples read)",
    "Setting default regularization parameter C=0.6140",
    "Optimizing..............done. (15 iterations)",
    "Optimization finished (maxdiff=0.00000).",
    "Runtime in cpu-seconds: 0.00",
    "Number of SV: 11 (including 6 at upper bound)",
    "L1 loss: loss=0.76660",
    "Norm of weight vector: |w|=0.99891",
    "Norm of longest example vector: |x|=1.50000",
    "Number of kernel evaluations: 386",
    "Writing model file...done"
  ]
}
```

# API

| Path                   | Methods   | Description                             |
|------------------------|-----------|-----------------------------------------|
| /                      | GET       | Information about SVM_SERVER commands.  |
| /model                 | GET       | Get a list of known models.             |
| /model/<name>          | GET       | Get informations connected to model <modelname>.|
| /model/<name>/train    | POST      | Create a new model called <modelname>.  |
| /model/<name>/predict  | GET/POST  | Create a prediction using model <modelname> and passed dataset.|
