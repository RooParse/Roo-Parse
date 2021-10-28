# Roo-Parse

This program was created to make tax returns easier and facilitate gathering of data so riders can see what the effects of changes in the algorithms are having on hourly rate over time.

<br />

## Download
***
You can download the latest release for Windows from Releases. Alternatively you can run directly from Python code  if you have Python installed on your machine (see below).


<br />

## Usage
***

1. Download all PDF invoices you wish to summarise and put them in the folder in your computer. Then, click on \"1. Select folder containing invoices\", navigate to the folder, and select it. Make sure there aren't any other files in the folder except for the invoices.
2. Click on \"2. Select folder to save data\" and select the directory you wish this programme to save the summarised results.
3. Click on \"3. Analyse and save summary\". It may take a few moments, but after the analysis is completed, a pop-up window will inform you if it was successful.
4. You can now access your summarised data in a ZIP file saved in the folder you specified.

<br />

## Run on any platform using Python
***
* [Install Python 3.7](https://www.python.org/downloads/release/python-379/)
* [Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* In powershell / bash:
```bash
git clone https://github.com/RooParse/Roo_Parse.git
cd Roo_Parse
pip3 install pipenv
python3 -m pipenv install
python3 -m pipenv run gui.py 
```
<br />

## License
***



Copyright (C) 2021  Workers' Observatory https://workersobservatory.org/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, version 3. This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

See terms and conditions [here](license.txt).

See the GNU Affero General Public License for more details. <https://www.gnu.org/licenses/>.