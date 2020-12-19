# Statistical analysis using iterative process

Dataset: Housing prices  
source: https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data

### Goal: Identify most important features affecting sale price  

---------------

The next steps are not sequential or mutually exclusive. 
For more details read the comments of the .ipynb file

## Data exploration
* Understanding the dataset   
    Shape/size  
    Columns labels & their meaning  
    Data types  
    Categorical features: which, what values they have, value count - output in **'categorical.txt'**  
    Descriptive statistics (mean, min, max, std, quartiles) - output in **'descriptiveStatistics.csv'** 
    

* NaN values  
    output in '**misingValues.txt**'  
    Looking at the missing values and data description, we see that the missing values are due to the absence of a characteristic - so in most cases NA can be replaced with 0. 

    Also a lot of columns are about quality or condition so their values can be substituted with numeric scale:   
    0: absent   
    1: very poor  
    2: poor   
    etc. 
    
* **Violinplots** for categorical features - Useful to see difference in means, quartiles, variances & distributions   
    - Based on the violinplots, the following variables appear to influence the sale price:
         - MSZoning
         - LandContour
         - Neighborhood
         - RoofMaterial
         - Certain types of Exterior1st & Exterior2nd
         - MasVnrType
         


## Compute field relationships scores 
Examine relationships between sales price and other features using:   

* **Linear correlation matrix** for numeric features  - visualize with **heatmap**  
    * Decide which features should be further investigated   

Check for normality - assumption of normal distribution in the different samples is not met &  
Homoscedacity also not met => neither ANOVA, Welch's ANOVA nor Kruskal Wallis can be used =>  
* **Mann-Whitney U test** on categorical values chosen from violin plots' evaluation (homegeneity of variance & normality is not met => )  
Check test's assumptions for number of data points - exclude features from the analysis that don't meet the criteria.   
Test was performed on all combinations of each categorical value. Results saved in **mannWhitneyP<a.txt** & **mannWhitneyP>a.txt** 


## Data cleaning & manipulation
* Distribution of 'sales price' is skewed.  
    Adjust using log transformation  
    Added new column to dataframe: 'AdjustedSalePrice'  
* Drop column 'MiscFeature' (96% values missing)
* Convert categorical data to numerical
* Fill misssing values with 0 - ok with this dataset   
    Check new status of missing values: none, hence **missingValues2.txt** is empty
* Based on MannWhitney results, convert the features that have no impact on saleprice with the more generic 'other' before creating dummy variables.
    However, since this is beyond the scope of the project, it is not shown here. 

## Feature reduction  
Decision based on results of correlation matrix, violinplots & anovas.  
Features with correlation over 0.5 were considered.  
eg. 'Overal quality' highly correlated with 'extrernal quality' & 
Overal quality's correlation with sale price is higher than external quality's correlation with sales price => External quality can be added to the feature reduction list.  
Correlations of top features can be found in **correlated.txt**

Features that don't have to be included in the model (removing them does not result in significant loss of information):
- External quality 
- GarageCars
- Kitchen quality 
- 1stFlrSF
- Full bath
- 1stFlrSF
- TotRmsAbvGrd

I have not dropped the features from the dataset, as this is not necessary for this project, since no machine learning will be used.  



# Conclusion
The important features are:   
1. 'OverallQual',
2. 'GrLivArea',
3. 'GarageArea',
4. 'TotalBsmtSF',
5. 'BsmtQual'
6. 'MSZoning'
7. Certain values of 'Neighborhood'
8. Certain values of 'LandContour'
9. Certain values of 'Exterior1st'
10. Certain values of 'Exterior2nd'

Potentially   
11. 'YearBuilt',  
12. 'YearRemodAdd'  

=> from 79 features present in our dataset we can focus on 10-12 of them. 
