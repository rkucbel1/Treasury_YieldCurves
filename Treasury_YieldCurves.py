#Parse Yield Curve from US Treasury Data:
import xml.sax
import requests
import json
import os

#SAX is a standard interface for event driven XML parsing
#Parsing XML with SAX requires ContentHandler by subclassing xml.sax.ContentHandler
#A ContentHandler object provides methods to handle parsing events
#The methods startDocument and endDocument are called at the start and end of the XML file
#The method characters(text) is passed the character data of the XML file via the parameter content

#The ContentHandler is called at the start and end of each element. If the parser is not in namespace mode,
#the methods startElement(tag, attributes) and endElement(tag) are called; otherwise the corresponding
#methods startElementNS and endElementNS are called

token = os.environ.get('PA_API_TOKEN')
database_url = os.environ.get('LINK_TYIELDS')
path_to_files = os.environ.get('PATH_TO_YIELD_FILES')

#Get the latest treasury data and save locally as xml file
url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=yieldyear&year=2021'
resp = requests.get(url)

with open(path_to_files + '/DailyTreasuryYieldCurveRateData.xml', 'wb') as foutput:
   foutput.write(resp.content)

#Define a XML handler
class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.date = []
        self.year2 = []
        self.year5 = []
        self.year10 = []
        self.year20 = []
        self.year30 = []

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "m:properties":
            print("----Rates----")

    def endElement(self, tag):
        if self.CurrentData == "d:NEW_DATE":
            print("Date: ", self.date[-1])
        elif self.CurrentData == "d:BC_2YEAR":
            print("2 Year: ", self.year2[-1])
        elif self.CurrentData == "d:BC_5YEAR":
            print("5 Year: ", self.year5[-1])
        elif self.CurrentData == "d:BC_10YEAR":
            print("10 Year: ", self.year10[-1])
        elif self.CurrentData == "d:BC_20YEAR":
            print("20 Year: ", self.year20[-1])
        elif self.CurrentData == "d:BC_30YEAR":
            print("30 Year: ", self.year30[-1])

        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "d:NEW_DATE":
            self.date.append(content)
        elif self.CurrentData == "d:BC_2YEAR":
            self.year2.append(content)
        elif self.CurrentData == "d:BC_5YEAR":
            self.year5.append(content)
        elif self.CurrentData == "d:BC_10YEAR":
            self.year10.append(content)
        elif self.CurrentData == "d:BC_20YEAR":
            self.year20.append(content)
        elif self.CurrentData == "d:BC_30YEAR":
            self.year30.append(content)

#Parse out treasury data
parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = XMLHandler()

parser.setContentHandler(Handler)
parser.parse(path_to_files + '/DailyTreasuryYieldCurveRateData.xml')

#get current date and format
current_date = Handler.date[-1]
current_date = current_date[:10]

#Get the latest data in the database to compare
url = database_url
data = requests.get(url)
yields_db = json.loads(data.text)
last_date = yields_db[-1]['date']

#If current_date = last_date, do nothing, else update the python anywhere database
if current_date == last_date:
    print('current_date:', current_date, 'is equal to last_date:', last_date, '- Database not updated')

else:

    headers = {'Authorization': token}

    payload = {
       'date': current_date,
       'Year_2': Handler.year2[-1],
       'Year_5': Handler.year5[-1],
       'Year_10': Handler.year10[-1],
       'Year_20': Handler.year20[-1],
       'Year_30': Handler.year30[-1],
    }

    resp = requests.post(url, headers=headers, data=payload)
    print(resp)
