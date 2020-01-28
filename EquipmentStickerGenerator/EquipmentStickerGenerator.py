from xml.etree import ElementTree as tree
import EquipmentStickerGeneratorHelpers as stickers
import argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument("-j", "--json", help="Location of equipment data JSON file for parsing")
parser.add_argument("-w", "--width", help="Sticker width (in pixels) - height is auto calculated to maintain 5:3 ratio")
parser.add_argument("-b", "--border", action='store_true', help="Draw a border around the outside of the label" )
parser.add_argument("-p", "--png", action='store_true', help='Store labels as PNG images (otherwise they will be SVGs)')

args = parser.parse_args()

if args.json is None:
    print("Please provide a JSON file")
    sys.exit(1)

if args.border is True:
    drawBorder = True
else:
    drawBorder = False

equipDict = stickers.parseJSON(args.json)

for tool in equipDict:
    toolName = equipDict[tool]['fulltext']
    toolURL = equipDict[tool]['fullurl']
    print(toolName)
    toolOwner = equipDict[tool]['printouts']['EquipOwner']
    if 'No' in equipDict[tool]['printouts']['EquipTrainingRequired']:
        toolAuthRequired = False
    else:
        toolAuthRequired = True

    if len(equipDict[tool]['printouts']['EquipZone']) == 0:
        toolZone = 'Zoneless'
    elif ':' in equipDict[tool]['printouts']['EquipZone'][0]['fulltext']:
        toolZone = equipDict[tool]['printouts']['EquipZone'][0]['fulltext'].split(':')[1]
    else:
        toolZone = equipDict[tool]['printouts']['EquipZone'][0]['fulltext']
        
    if args.width is None:
        thisSticker = stickers.Sticker(drawBorder, toolName, toolOwner, toolURL, toolAuthRequired, toolZone)
    else:
        thisSticker = stickers.Sticker(drawBorder, toolName, toolOwner, toolURL, toolAuthRequired, toolZone, int(args.width))
    
    thisSticker.saveSVG(toolName)
    
    if args.png:
        thisSticker.savePNG(toolName)


sys.exit(0)