# Readme

`datasets` folder contains the datasets we use, they are pre-processed for input.

`src` folder is for the source codes, `src/Solvers` contains .py and .jar solvers and source codes for .jar are in `src/Solvers/MOEA`.

Files in `tasks` are the configs for a certain problem solved by a certain algorithm. During processing, `dump` folder would be generated which contains the intermediate config for .jar solver. Finally the results would be found in `results`.

`run.py` shows how to get the results and give an analysis on them.

