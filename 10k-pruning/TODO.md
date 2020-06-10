# Convert CSV

# TODO

- [x] recieve H&P paper from Tobias
- recieve corpus CSV from Tobias
  - [x] download first 500 papers
  - [x] download full corpus (takes hours?)
- [x] recieve Compustat data from Tobias
- [x] implement parser and writer for corpus CSV format
- [x] implement H&P pruning in python
- produce H&P-pruned corpus CSV
  - [x] first 500 papers
  - [x] full corpus (takes hours?)

# Overview
- read paper where they specified how they pruned data in original boolean model (H&P - hobert & philips)
	- Tobias will send
- get data from Reed server to start pruning
- save old data and take new data and compare results to see if more or less data was better
- mimic the process the other paper claimed to have done
	- compare result of this process to actual data set they ended up with (the companies they kept in)
- make pruned version of our data base that matches what companies they kept

# 2010 H&P Paper Methodology

> Our full sample of 10-Ks from 1997–2008 comprises 68,302 observations; this declines to 63,875 when we exclude firms without valid Compustat data, firms with nonpositive sales, or firms with assets of less than $1 million. This declines further to 50,673 if we additionally require 1 year of lagged Compustat data and exclude financial firms (SIC codes in the range 6000–6999).

1. Full sample of 10-Ks from 1997-2008 starts with 68,302
2. Declines to 63,875 by excluding:
   - firms without Compustat data
   - firms with nonpositive sales
   - firms with assets of less than $1 million
3. Declines to 50,637 by excluding:
    - firms without 1 year of lagged Compustat data
    - financial firms
