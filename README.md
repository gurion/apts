A simple web scraper to get apartment data.

To use:
1. Make sure all requirements are installed
	* If not, run `pip install -r requirements.txt`
2. run `python scraper.py`
3. You will be prompted for a unique search ID. This is the ID associated with the specific map or search region you're looking at. Examples may include:
	* ?sk=115ada7c860d92c4bc132f69f6ac8e45&bb=33imuxg3vHz4y4lC
	* new-york-ny
4. Output is put into a csv file called apts.csv in the directory in which you're running the script
5. There are still errors I'm working on. As of now, these are printed to console, and you will be able to see the address at which there was an error, or the URL on which there was an error.
