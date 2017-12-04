# TWDE-Datalab
![](http://i0.kym-cdn.com/photos/images/original/001/268/288/04a.gif)

This is the onboarding document for the TWDE Datalab. If you want to get involved, find something confusing, or just want to say hi, [please open an issue](https://github.com/emilyagras/kaggle-favorita/issues).

1. [Introduction](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#introduction)
1. [Data](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#data)
1. [Infrastructure](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#infrastructure)
1. [Algorithms](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#algorithms)
1. [Next Steps](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#next-steps)
1. [Getting Started](https://github.com/emilyagras/kaggle-favorita/blob/master/README.md#getting-started)


## Introduction
The purpose of this project is to help build a foundational knowledge pool around the fields of data science, machine learning, and intelligence empowerment for ThoughtWorkers in Germany. To do so, we've selected a competition from kaggle.com that, broadly speaking, compares to a realistic problem we could provide for clients. The specific problem is demand forecasting for an Ecuadorian grocery store company. For more specifics, see [the Favorita Grocery Sales Forecasting Kaggle competition](https://www.kaggle.com/c/favorita-grocery-sales-forecasting)

## Data

We've been provided [4 years of purchasing history](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data) in the competition itself. Our goal is to analyze this data, plus any other data we acquire (see the [external data discussion on kaggle](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/discussion/41537)), and produce an estimated `unit sales` for each item in each store on each day for a two week period in 2017. 


## Infrastructure

Our workflow is divided into several jobs, which can be deployed one after another automatically on Amazon Web Services. Let's look at Arif's amazing diagram to illustrate the workflow.

![](https://user-images.githubusercontent.com/8107614/33561247-72463dd0-d912-11e7-8485-b40585da8434.png)





## Algorithms

## Next Steps

## Getting Started

# notes for setup
I recommend using anaconda to set up environment using environment.yml

Yet, sometimes necessary latest version is not available. Then please use pip in addition. 
for example,
pip install notebook==5.1.0
