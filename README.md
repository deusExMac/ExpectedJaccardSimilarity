# About

Attempts to solve (and verify) empirically Exercise 3.1.3 page 86 found in [1] which states:

_"Suppose we have a universal set U of n elements, and we choose two subsets S and T at random, each with m of the n elements. What is the expected value of the Jaccard similarity of S and T ?"_

It does this by sampling from the universal set and calculating the Jaccard similarities a number of times and averaging the calculated similarities. This average is considered a solution to the exercise since it converges to the expected value. It also attempts to verify that the average converges to the exact solution of exercise 3.1.3. 

The solution of exercise 3.1.3, i.e. the expected value of the Jaccard similarity, is given by the formula:

$$E\left(\\text{Jaccard similarity}\right) = \sum_{k=0}^{m} \left(k\over 2m-k\right) \frac{{C}^n_k {C}^{n-k}_{m-k} {C}^{n-m}_{m-k}} {{C}^n_{m}{C}^n_{m}} \ \ \ \ \ \ \ [1]$$ 

where $$n$$ the number of distinct elements in the Universal set, $$m$$ the number of  elements in sets S and T, and $${C}^{n}_{k}$$ the binomial coefficient i.e. number of ways to choose a subset of $$k$$ items from a larger set of $$n$$ items (number of combinations) which is equal to $$\frac{n!}{\left(n-k\right)!k!}$$ .

The script implements the general case where the number of elements in sets S and T are not necessarily equal. In that case the expected Jaccard similarity is equal to: 

$$E\left(\\text{Jaccard similarity}\right) = \sum_{i=0}^{min\left(m_1, m_2\right)} \left(i\over m_1+m_2-i\right) \frac{{C}^n_i {C}^{n-i}_{min\left(m_1, m_2\right)-i} {C}^{n-{min\left(m_1, m_2\right)}}_{max\left(m_1, m_2\right)-i}} {{C}^n_{m_1}{C}^n_{m_2}} \ \ \ \ \ \ \ [2]$$ 


where $$n$$ the number of distinct elements in the Universal set, $$m_1$$ the number of distinct elements in ths S set,  $$m_2$$ the number of distinct elements in the T set and $${C}^{n}_{k}$$ the binomial coefficient i.e. the number of ways to choose a subset of $$k$$ items from a larger set of $$n$$ items (number of combinations) which is equal to $$\frac{n!}{\left(n-k\right)!k!}$$ . 

For a proof of the above formulas, see file Exercise 3.1.3 Solution.pdf . 

The script averages the Jaccard similarities of randomly sampled sets S and T from the universal set U a number of times and checks if it converges to the expected value. Convergence of the average to the expected value (output of the formula above) is done visually using an animated plot. Alternativelly, convergence using an user-defined epsilon threshold is also supported.

The script supports a number of settings to make testing easier. If the script is executed without any arguments the following default values will be in effect: |U|=100, |S|=20, |T|=20 n=100 (100 iterations i.e. 100 random sets of pairs S and T generated and their Jaccard similarities calculated - the average is reported as the expected Jaccard similarity). With these settings, the exact expected value of the Jaccard similarity is 0.11336428141466905 and the script checks if the average Jaccard similarity converges to that value. Arguments allows script execution with different settings such as different sizes of sets S, T, U, number of iterations etc (See Arguments section).  The script requires some third party Python modules installed to execute properly that can be found in file requirements.txt .
   
This approach was based on an initial idea by Ioannis Refanidis (https://www.uom.gr/en/yrefanid) who did a first implementation for confirming empirically the theoretically proven value for specific values for U, S and T. This motivated me to do a Python implementation which gave me also the opportunity to experiment with the animation capabilities of matplotlib (which i always wanted anyway).

_I apologize for the apparent complexity of the script. Since i had some time to spare, i tried to play around with different parameters to verify the results. This might look a little overengineered and you are probably right but as mentioned, there was some time to spare._
_This code has parts that can and should be improved and refactored._

_I apologize for any error or bug that you may encounter. Any errors, bugs, mistakes, bad designs or omissions in this material are my responsibility alone._

# Required modules
See file requirements.txt  


# Arguments
The following configuration settings are supported. These can be given in the form of command line arguments and/or as settings in a config file. 
Precedence is as follows: 
* Default configuration values (consts inside scripts) are overridden by settings in the configuration file if it exists. Script searches for configuration files named 'ejv.conf', 'jaccard.conf', 'expectedjaccard.conf' (in that order) and loads the first one that it finds.
* Configuration file settings are overridden by command line arguments if provided.


Settings below are presented in the form of < command line argument > | < name in configuration file >:

``-u integer | universalsetsize``: Number of distinct items in the universal set, out of which sets will be randomly drawn. If this value is greater than 100, the maxvalue must be set at least to the same value. Defaults to 100.

``-s integer | ssetsize``: Size of set S. Defaults to 20.

``-t integer | tsetsize``: Size of set T. Defaults to 20.

``-n integer | nsamples``: Number of S and T set pairs to generate and calculate their Jaccard similarity. Equivalently, how many iterations to do calculating Jaccard similarities. This is one stopping condition of the script. Defaults to 100.

``-j [custom | sklearn] | jaccardmode``: Determines how the Jaccard similarity will be calculated: using the definition (custom) i.e. intersection over union of sets  or using sklearn. sklearn's method requires the sets to be one-hot encoded. Both ways return the same Jaccard similarity for the same sets. Defaults to custom.  

``-m integer | maxvalue``: Maximum value of universe set. This value must be at least as large as the size of the universal set (universalsetsize setting). Defaults to 100


``-T float | targetexpectedjaccardsimilarity``: The reference Jaccard similarity to check average against. Depending on its value, 
*  $\geq 0$: the value as entered is used as reference.
* $= -1$: the exact theoretically Jaccard similarity is calculated using the derived formula and set as reference.
* $\\text{any other value} \lt 0 $: no reference value is set.

Reference value is also displayed on plot. Defaults to -1 .

``-e float | epsilon``: Maximum allowed tolerance between current average and target expected value of Jaccard similarity (as specified by targetexpectedjaccardsimilarity setting). If tolerance falls below epsilon a number of times (see deltastreak option), script terminates. This is another stopping condition of the script. If both nsamples (-n) and epsilon (-e) are set, nsamples is ignored. Defaults to -1 which means no e.

``-k integer | deltastreak``: Number of consecutive times difference of current average and target expected value of Jaccard similarity (targetexpectedjaccardsimilarity) must fall below epsilon (e) before terminating. Defults to 3.

``-U | uniformitycheck``: If set, does a check to see if the randomly generated sets S and T follow a uniform distribution. Provides a visual evidence for uniform distribution of the generated sets after script finishes. Defaults to False.

``-A | autoterminate``: If set the script closes the plot and terminates without user intervention. Otherwise, plot window will remain visible and open until the user closes it by pressing return on the console or execution window. Defaults to False.

``-ws integer | windowsize``: Window size to plot on animated chart i.e. number of last calculated values to plot on chart. Defaults to 50.

``-V | showvalues``: If set, the Jaccard similarity will appear on the animated chart for every 10th point.

``-S | savesimilarities``: If set, the Jaccard similarities calculated will be stored in a csv file. Name of the outputfile can be specified by the -o option. If no file name is specified, it defaults to jaccardSimilarities< size of S set > x < size of T set> x < size of Universal set >. csv  . Appends to file, if output file already exists.

``-o string | outputcsvfile``: Specifies the prefix of the file name to store jaccard similarities. File name is completed by concatenating to prefix the size of S set, size of T set and size of U set. Can also be a path; if directories in specified path do not exist, these will be created. Defaults to jaccardSimilarities .

``-P | saveplot``: If set, the plot after the last pair has been processed is saved to a file. The default format is png . Currently the plot is saved in a file with name having the form ``Execution_<S set size>x<T set size>x<Universal set size>``

``-F | plotpdf``: If set, the plot is saved as pdf with the default file name 

``-f [sset | tset] | fields-list``: Additional data to store in output csv file together with the Jaccard similarity. Currently only the randomly generated S and T set are supported with this flag. Can add multiple times e.g. -f sset -f tset to store also the S and T sets into the csv file. By default, these sets are not stored in the output file.

# Test runs
When executing the script, an animated plot [like this](https://github.com/deusExMac/ExpectedJaccardSimilarity/blob/main/Execution_20x20x100.png) will show up.

Below some results from test runs. In the table below, columns should be interepreted as follows: 

* |U| : size of universal set
* |S| : size of S set
* |T| : size of T set
* n   : number of iterations (displays the actual number of iterations if epsilon was set)
* e   : epsilon - maximum allowed tolerance (-1 if number of iterations was used. NOTE: epsilon has precedence)
* Average Jaccard similairity: the average calculated by the script
* Expected Jaccard similarity: the expected Jaccard similarity calculated by [1]
* delta: diffence between average and expected Jaccard similarity

Executing the script with various parameters and settings returned the following:


| \|U\| | \|S\|    | \|T\|    | n    | e    | Average Jaccard similarity  | Expected Jaccard similarity  | Delta  |
| :---:   | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 100| 20| 20| 100| -1| 0.11017634653857564 | 0.11336428141466905 | 0.00318 |
| 100 | 20 | 20 | 500 | -1 | 0.10885766709186263 | 0.11336428141466905 | 0.00450 |
| 100 | 20 | 20 | 1000 | -1 | 0.11246304040908554 | 0.11336428141466905 | 0.00090 |
| 100 | 20 | 20 | 2000 | -1 | 0.11437086914241613 | 0.11336428141466905 | 0.00100 |
| 100 | 20 | 20 | 5000 | -1 | 0.11242762689638251 | 0.11336428141466905 | 0.00093 |
| 100 | 20 | 20 | 1868 | 0.0008 | 0.11415980763823749 | 0.11336428141466905 | 0.00079 |
| 100 | 30   | 30   | 100   | -1   | 0.18803981406511244   | 0.1785022900543863   | 0.00953   |
| 100 | 30   | 30   | 500   | -1   | 0.18038402866706307   | 0.1785022900543863   | 0.00188   |
| 100 | 30 |30 | 1000| -1 | 0.17940429007341643 | 0.1785022900543863 |0.000902 |
| 100 | 30 |30 | 5000| -1 | 0.17865630501767044 | 0.1785022900543863 | 0.00015 | 
| 100 | 20   | 40   | 100   | -1   | 0.1501863356521875   | 0.15551227322305258   | 0.00532   |
| 100  | 20   | 40  | 500   | -1   | 0.15382249766285738  | 0.15551227322305258   | 0.00168   |
| 100  | 20   | 40  | 1000  | -1   | 0.15719421563960867  | 0.15551227322305258   | 0.00168   |
| 100 | 20   | 40   | 10000   | -1   | 0.15512681592625022   | 0.15551227322305258   | 0.00038   |
| 100 | 20   | 40   | 351   | 6e-05   | 0.15546220140392897   | 0.15551227322305258   | 5.00718e-05   |
| 100 | 20   | 40   | 4036  | 3e-06   | 0.15551646749741826   | 0.15551227322305258   | 4.19427e-06   |
| 100 | 20   | 40   | 5178   | 6e-07   | 0.15551291751256643   | 0.15551227322305258   | 6.44289e-07   |
| 100 | 8   | 12   | 17977   | 5e-07   | 0.052790079590535485   | 0.0527905108745123   | 4.31283e-07   |
| 50  | 10  | 20   | 2000    | -1      | 0.1565475473343914     | 0.1572349497856148   | 0.00068       |
| 500 | 150 | 230  | 500     | -1      | 0.22232728758201706    | 0.22219540443881813  | 0.00013       |
| 80  | 24  | 44   | 5000    | -1      | 0.2423565298116981     | 0.2426217112571133   | 0.00026  |












# References
1. Leskovec, J., Rajaraman, A., and Ullman, J. D.: Mining of Massive Datasets, 3rd Edition, Cambridge University Press, 2014. Available http://mmds.org
