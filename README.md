# py_valuenormalization

This package provides some basic necessary tools to do attribute value normalization and string clustering in data cleaning and integration pipelines.

## Important Note ##

At the moment, due to incompatibility of Linux and Mac versions of PyQt5 package, we have two separate branches for Linux and Mac user interfaces. The ```master``` branch contains the version which works on Linux and the ```pyqt5mac-dev``` branch contains the version which works in Mac.

## Installation Guide ##

To install this package:

1. First install PyQt4, e.g. using one of the following methods:

  1. If you have Anaconda installed on your machine, then use the following command:

     ```$ conda install pyqt```

  2. Otherwise follow the instructions at http://pyqt.sourceforge.net/Docs/PyQt4/installation.html

2. Then install the package using one of the following methods:

  1. Run the following command:

     ```pip install git+https://github.com/adelaneh/py_valuenormalization.git```
	 
  2. First clone the package source code using the following command:

     ```$ git clone https://github.com/adelaneh/py_valuenormalization```

     Then enter the source code root folder (```py_valuenormalization```) and install the package using the following command:

     ```$ python setup.py install```

     You can use ```--prefix``` to change the destination folder for installing the package (see the help using ```$ python setup.py --help```).

## Usage Guide ##

To use this package, import it by running the following python command:

   ```>>> import py_valuenormalization as vn```

We have developed two main approaches to normalize values, namely:

1. Manual value normalization
2. Clustering-based value normalization

### Manual Value Normalization ###

In manual value normalization, you merge values into clusters to normalize them:

1. First load your data values into a list using the following command:

   ```>>> vals = vn.read_from_file('PATH-TO-TEXT-FILE')```
  
   where the file at ```PATH-TO-TEXT-FILE``` contains the values to be normalized, one data value per line. You can download one of our sample datasets from https://github.com/adelaneh/py_manual_vn/tree/master/py_valuenormalization/data.

2. Now run the command:

   ```>>> res = vn.normalize_values(vals)```
  
   This will open the value normalization application which gives you instructions on how to normalize the input values.

3. Finally when you finish the normalization process and close the above application, the normalization results are returned in the variable ```res```: it is a dictionary where each key is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster.

### Clustering-based Value Normalization ###

#### Clustering the Values ####

In clustering-based value normalization, you first cluster the values using one of the following three method:

1. Regular hierarchical agglomerative clustering (HAC)
2. Smart clustering, which finds the best HAC parameter settings using input training data
3. Hybrid clustering, which finds a clustering of input values such that you need to spend minimal time to clean up the clustering

To cluster the values, follow these steps:

1. First load your data values into a list using the following command:

   ```>>> vals = vn.read_from_file('PATH-TO-TEXT-FILE')```
  
   where the file at ```PATH-TO-TEXT-FILE``` contains the values to be normalized, one data value per line. You can download one of our sample datasets from https://github.com/adelaneh/py_manual_vn/tree/master/py_valuenormalization/data.

2. Then use one of the following sequences of commands to cluster the values:

    1. Regular HAC: 

         ```>>> hac = vn.HierarchicalClustering(vals)```

         ```>>> clusts = hac.cluster(sim_measure = '3gram Jaccard', linkage = 'single', thr = 0.7)```

         where ```vals``` is the set of input values, ```sim_measure```, ```linkage``` and ```thr``` are standard HAC parameters, and ```clusts``` is a dictionary where each key is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster.

    2. Smart clustering:

        ```>>> (_, training_pairs) = vn.calibrate_normalization_cost_model(vals)```

        ```>>> smc = vn.SmartClustering(vals, training_pairs)```

         ```>>> (clusts, best_setting) = smc.cluster()```

        where ```training_pairs``` is a dictionary where each key is a value pair ```(v1, v2)``` with ```v1``` and ```v2``` being distinct input values, and the corresponding value is ```True``` if ```v1``` and ```v2``` refer to the same entity and ```False``` otherwise.

        The output consists of a dictionary ```clusts``` and a tuple ```best_setting```. Each key of the dictionary ```clusts``` is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster. ```best_setting = (agrscore, simk, lnk, thr)``` is a tuple of agreement score and HAC parameter settings using which ```clusts``` is obtained. ```agrscore``` is the agreement score between ```clusts``` and ```training_pairs```; i.e. the fraction of the value pairs in ```training_pairs``` which agree with ```clusts```. ```sim_measure```, ```linkage``` and ```thr``` are the standard HAC parameters settings using which ```clusts``` is obtained.

    3. Hybrid clustering:

        ```>>> (cm, _) = vn.calibrate_normalization_cost_model(vals)```

        ```>>> hybhac = vn.HybridClustering(vals, cm)```

        ```>>> (clusts, mcl) = hybhac.cluster()```

        where ```cm``` is a cost model used by hybrid clustering algorithm to find the clustering of the input data set that requires minimum effort by you to clean it up.

        The outpurt consists of a dictionary ```clusts``` and an integer ```mcl```. Each key of the dictionary ```clusts``` is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster. ```mcl``` is the maximum size of the clusters in ```clusts```. 

#### Cleaning Up the Clusters ####

Now you can clean up the clusters obtained above to arrive at the correct clustering of the input values. This phase consists of two main steps:

1. Split step, where you split clusters containing values referring to more than one real-world entity into smaller clusters each of which contains values referring to a single entity 
2. Merge steps, in which you merge clusters referring to the same entity

To clean up the clustering results run the following command:

```>>> clean_clusts = vn.normalize_clusters(clusts)```

where ```clusts``` is a dictionary where each key is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster. This will open a graphical user interface to clean up ```clusts``` and the results with be returned in ```clean_clusts``` which is a dictionary where each key is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster.

