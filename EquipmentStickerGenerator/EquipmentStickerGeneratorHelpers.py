#from xml.etree import ElementTree as tree
import lxml.etree as tree
import qrcode, json, os

DEF_TOTAL_WIDTH = 1000   # Width of the sticker (in pixels)
DEF_TOTAL_HEIGHT = 3*DEF_TOTAL_WIDTH/5  # Height of sticker in pixels (5:3 ratio assumed)

# A lot of metadata is included with the MediaWiki JSON export, we only care about the results of the query though
def parseJSON(fName):
    with open(fName, 'r') as fptr:
        equipList = json.load(fptr)
    return equipList['results']


class Sticker:
    def __init__(self, drawBorder, toolName, ownerName, url, authRequired, zone, width=DEF_TOTAL_WIDTH):
        self.width = width  # Either the width specified as an argument by the user or the default if none is given
        self.height = 3*width/5 # Height is automatically calculated to maintain aspect ratio
        self.hugeFontSize = 50*(width/1000) # Font size used for tool name
        self.bigFontSize = 40*(width/1000)  # Used for zone and owner headings and auth status
        self.mediumFontSize = 32*(width/1000)    # Used for actual zone and owner names
        self.smallFontSize = 26*(width/1000)
        self.curveRadius = 25*(width/1000)    # Radius on auth box curves
        self.dwg = tree.Element('svg', width=str(self.width), height=str(self.height), 
            version='1.1', xmlns='http://www.w3.org/2000/svg')

        if drawBorder:  # Useful when looking at the label on a screen, don't want it for 
            self.drawBorder()
        
        self.addToolName(toolName)
        self.addQR(url, self.getSafeToolName(toolName))
        self.addAuth(authRequired)
        self.addZone(zone)
        self.addOwner(ownerName)
        self.addURL(url)

    # If desired, draw a border around the label (used for development) 
    def drawBorder(self):
        border = tree.Element('rect', x='0', y='0', width='100%', height='100%', 
            fill='none', stroke='black')
        self.dwg.append(border)

    # Zone label and actual zone name, splits on spaces if name is too long, works for all zone names as of Jan 26, 2020
    def addZone(self, zoneName):
        #TODO: Check length of zone name and split into multiple lines if required
        zoneText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.62),  fill='black', 
            style='font-family:Arial;font-size:'+str(self.bigFontSize)+'px;font-weight:bold;text-anchor:middle;')
        zoneText.text = 'Zone:'
        self.dwg.append(zoneText)
        if len(zoneName) <= 16:
            zoneText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.69),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:middle;dominant-baseline:top')
            zoneText.text = zoneName
            self.dwg.append(zoneText)
        else:
            splitIndex = getClosestChar(zoneName, ' ', 16)
            zoneText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.69),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:middle;dominant-baseline:top')
            zoneText.text = zoneName[0:splitIndex]
            self.dwg.append(zoneText)
            zoneText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.76),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:middle;dominant-baseline:top')
            zoneText.text = zoneName[splitIndex+1:]
            self.dwg.append(zoneText)

    # Draw a box, add a label, and indicate whether authorization is required or not
    def addAuth(self, authRequired):
        authRect = tree.Element('rect', x=self.convert('X', 0.65), y=self.convert('Y', 0.25), rx=str(self.curveRadius), width=self.convert('X', 0.3), height=self.convert('Y', 0.25),
            fill='none', stroke='black')
        self.dwg.append(authRect)

        authText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.35),  fill='black', 
            style='font-family:Arial;font-size:'+str(self.bigFontSize)+'px;text-anchor:middle;dominant-baseline:top')
        authText.text = 'Authorization'
        self.dwg.append(authText)

        authText = tree.Element('text', x=self.convert('X', 0.8), y=self.convert('Y', 0.42),  fill='black', 
            style='font-family:Arial;font-size:'+str(self.bigFontSize)+'px;text-anchor:middle;font-weight:bold')
        if authRequired:
            authText.text = 'Required'
        else:
            authText.text = 'Not Required'
        self.dwg.append(authText)

    # QR code linking to tool wiki page
    def addQR(self, url, fName):
        qrObject = qrcode.QRCode(border=1)
        qrObject.add_data(url)

        img = qrObject.make_image()
        #img.save(fName+'_QR.png')
        img.save(os.path.join('Images', 'QR', fName+'_QR.png'))
        qrCode = tree.Element('image', x=self.convert('X', 0.02), y=self.convert('Y', 0.19), width=self.convert('X', 0.4), height=self.convert('Y', 0.66))
        qrCode.set("{http://www.w3.org/1999/xlink}href", os.path.join('Images', 'QR', fName+'_QR.png'))
        self.dwg.append(qrCode)

    # Tool name in big print, bolded and centered
    def addToolName(self, toolName):
        if len(toolName) <= 30:
            toolNameText = tree.Element('text', x=self.convert('X', 0.5), y=self.convert('Y', 0.14),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.hugeFontSize)+'px;font-weight:bold;text-anchor:middle;')
            toolNameText.text = toolName
            self.dwg.append(toolNameText)
        else:
            splitIndex = getClosestChar(toolName, ' ', 30)
            toolNameText = tree.Element('text', x=self.convert('X', 0.5), y=self.convert('Y', 0.1),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.hugeFontSize)+'px;font-weight:bold;text-anchor:middle;')
            toolNameText.text = toolName[0:splitIndex]
            self.dwg.append(toolNameText)

            toolNameText = tree.Element('text', x=self.convert('X', 0.5), y=self.convert('Y', 0.18),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.hugeFontSize)+'px;font-weight:bold;text-anchor:middle;')
            toolNameText.text = toolName[splitIndex+1:]
            self.dwg.append(toolNameText)

    # Owner image, label, and name - If multiple owners prints first in list and a generic second line
    def addOwner(self, ownerName):
        if 'i3' in ownerName[0]:   # i3Detroit Logo for image
            ownerImage = tree.Element('image', x=self.convert('X', 0.43), y=self.convert('Y', 0.25), width=self.convert('X', 0.2), height=self.convert('Y', 0.3))
            ownerImage.set("{http://www.w3.org/1999/xlink}href", os.path.join("Images", "Non-Equipment","i3_logo.png"))
        else:   # Generic image
            ownerImage = tree.Element('image', x=self.convert('X', 0.43), y=self.convert('Y', 0.25), width=self.convert('X', 0.2), height=self.convert('Y', 0.3))
            ownerImage.set("{http://www.w3.org/1999/xlink}href", os.path.join("Images", "Non-Equipment", "OtherOwner_logo.png"))

        self.dwg.append(ownerImage)

        ownerText = tree.Element('text', x=self.convert('X', 0.53), y=self.convert('Y', 0.62),  fill='black', 
            style='font-family:Arial;font-size:'+str(self.bigFontSize)+'px;font-weight:bold;text-anchor:middle;')
        ownerText.text = 'Owner:'
        self.dwg.append(ownerText)

        ownerText = tree.Element('text', x=self.convert('X', 0.53), y=self.convert('Y', 0.69),  fill='black', 
            style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:middle;')
        ownerText.text = ownerName[0]
        self.dwg.append(ownerText)

        if len(ownerName) > 1:
            ownerText = tree.Element('text', x=self.convert('X', 0.53), y=self.convert('Y', 0.76),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:middle;')
            ownerText.text = 'and others'
            self.dwg.append(ownerText)

    # Human readable URL (same address as QR code)
    def addURL(self, url):
        if len(url) > 55:
            splitIndex = url.find('wiki/')+len('wiki/')
            urlText = tree.Element('text', x=self.convert('X', 0.03), y=self.convert('Y', 0.9),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:left;')
            urlText.text = url[:splitIndex]
            self.dwg.append(urlText)

            urlText = tree.Element('text', x=self.convert('X', 0.03), y=self.convert('Y', 0.96),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:left;')
            urlText.text = url[splitIndex:]
            self.dwg.append(urlText)
        else:
            urlText = tree.Element('text', x=self.convert('X', 0.03), y=self.convert('Y', 0.93),  fill='black', 
                style='font-family:Arial;font-size:'+str(self.mediumFontSize)+'px;text-anchor:left;')
            urlText.text = url
            self.dwg.append(urlText)

    # Inkscape and other SVG editors don't like percentage-based locations and the XML builder module likes strings.  Values returned in pixels
    def convert(self, axis, percent):
        if percent > 100:
            percent = percent/100

        if axis.upper() == 'X':
            return str(int(self.width*percent))
        elif axis.upper() == 'Y':
            return str(int(self.height*percent))

    # Generate the sticker SVG
    #TODO: Also create the PNG from this and delete the SVG, QR code images, etc.
    def saveSVG(self, fName):
        fName = self.getSafeToolName(fName)

        if not fName.endswith('.svg'):
            fName = fName+'.svg'

        with open(fName, 'wb') as fptr:
            fptr.write(tree.tostring(self.dwg, pretty_print=True))

    def savePNG(self, pngName, keepSVG):
        pngName = self.getSafeToolName(pngName)

        if not pngName.endswith('.png'):
            pngName = pngName+'.png'

        svgName = pngName.replace('.png', '.svg')

        os.system('inkscape %s -b white -e %s'%(svgName,pngName))

        if not keepSVG:
            os.remove(svgName)

    # Remove characters that aren't safe for file names before generating QR code images or final SVGs
    def getSafeToolName(self, toolName):
        for char in [' ', '\\', '/', '(', ')', '"']:
            toolName = toolName.replace(char, '_')

        return toolName

# Find the closest instance of a specified character to a given index in a provided string - Returns the index
def getClosestChar(string, char, idx):
    lowHalf = string.rfind(char, 0, idx)
    highHalf = string.find(char, idx, len(string)-1)

    if abs(idx-lowHalf) < abs(idx-highHalf):
        return lowHalf
    else:
        return highHalf

# Check if Inkscape is installed on the system - The CLI is used to convert SVG -> PNG
# True if inkscape is present, False otherwise
def checkInkscape():
    result = os.system('inkscape --version')

    return not bool(result)