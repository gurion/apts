## Web scraper to get apartment data from apartments.com.

#### To use:
1. Make sure all requirements are installed
	* If not, run `pip install -r requirements.txt`
2. run `python scraper.py` on command line. This is written in python 3 so check your version. 
3. You will be prompted for a unique search ID. This is the ID associated with the specific map or search region you're looking at. Examples may include:
	* ?sk=115ada7c860d92c4bc132f69f6ac8e45&bb=33imuxg3vHz4y4lC
	* new-york-ny
4. If the extension used is a unique search region or polygon search, like the former, input 1 when prompted. Otherwise input 0.
5. Output is put into a csv file with user input file name in the directory in which you're running the script. Leave out the extension when entering the file name (`test` rather than `test.csv`)
6. If there are any errors they will be printed at the end of the script. 

#### CSV fields
Field   	| Notes 
----------- | ------------- 
address 	| full street address of the property  
unit    	| unit number - will be N/A if not found, often properties list it as 1 bed/1 bath rather than actual number     
beds		| number of bedrooms
baths		| number of bathrooms
rent		| monthly rent - if there is a range given the average of the range is taken
sqft		| square footage of the apartment
avail		| availability. 0 if unavailable, 1 if available, 2 if will be available at a future date
pets		| pet policies. given as a semicolon separated list
parking		| parking available at property
built		| year in which building was built
renovated	| year building renovated if applicable
num_units	| number of units in the building
stories		| number of floors in the building
fitness		| fitness facilities available
outdoor		| outdoor space available

#### To Do:
- [ ] Send requests through rotating proxy
- [ ] Integrate into server as backend for web app
