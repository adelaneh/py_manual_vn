#py_manual_vn

To use this package:

1. First import the package by running:
```>>> import py_manual_vn as manvn```
2. Then load your data values into a list using the following command:
```>>> vals = manvn.read_from_file('PATH-TO-TEXT-FILE')```
where the file at PATH-TO-TEXT-FILE contains the values to be normalized, one data value per line.
3. Now run the command:
```>>> res = manvn.normalize_values(vals)```
This will open the value normalization application which gives you instructions on how to normalize the input values.
4. Finally when you finish the normalization process and close the avoce application, the normalization results are returned in the variable ```res```: it is a dictionary where each key is the label of a cluster of data values, and the corresponding value is the set of data values in this cluster.
