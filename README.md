# Probing Language Models for Analysis of Temporal Expressions

This repository contains the code and three temporal NLI datasets that were presented in _Probing Language Models for Analysis of Temporal Expressions_ by Shivin Thukral, Kunal Kukreja and Christian Kavouras.

All three datasets with their corresponding _train_ and _test_ splits, on which the models were trained/tested and results produced in the paper, are present under the `data` directory. The code which was used to create these datasets is present in the `code` directory. 

To run the code and create Challenge Set 1 afresh:
```
cd code
python cs1.py
```
The same procedure needs to be followed for the other challenge sets.
Note that though this might create a dataset with the same format, the instances might be different from what were used for training and testing purposes in our experiments.
