from rules import *
import sys
import argparse

rulesModule = None

def importRules(configurationFilename):
	global rulesModule
	rulesModule = __import__("rules")
	rulesModule.importConfiguration(configurationFilename)

def nextWord(text, withSpace):
	if not withSpace:
		text = text.strip()
	word = ""
	if len(text) == 0:
		return ""
	if text[0] in "{([])}":
		return text[0]
	isAlpha = (text[0].isalpha() or (text[0] in "#"))
	isSpace = text[0] in " \t\n"
	for char in text:
		if ((char in " \t\n") == isSpace) and ((char.isalpha() or (char in "#")) == isAlpha) and (char not in "{([])}") and not (char not in "\"" and len(word) > 0 and word[-1] in "\""):
			word += char
		else:
			return word
	return word

def nextLine(text):
	line = ""
	for char in text:
		if char != '\n':
			line += char
		else:
			return line
	return line

def ifLineIsComment(text):
	if len(text) < 2:
		return False
	return text[0] == "/" and text[1] == "/"

def checkWords(prevWord, spaces, nextWord):
	for rule in rulesModule.allRules:
		isApplied, space = rule.apply(prevWord, spaces, nextWord)
		if isApplied:
			return space
	# if no rule was applied, actually should not be called
	return spaces

def formatFile(filename, outputFilename):
	file = open(filename)
	text = file.read()
	file.close()

	allSpaces = " \n\t"
	result = ""
	iter = 0
	word = ""
	while iter < len(text):
		prevWord = word
		isPrevSpace = prevWord[0] in allSpaces if len(prevWord) > 0 else False
		word = nextWord(text[iter:], True)
		if len(word) == 0:
			break
		nextChar = text[iter + len(word)] if (iter + len(word) < len(text)) else ""
		isSpace = word[0] in allSpaces
		isAlpha = word[0].isalpha() or word[0] == "#"
		isOperator = not isSpace and not isAlpha

		if isSpace:
			result += checkWords(prevWord, word, nextWord(text[iter:], False))
			if '\n' in word:
				# check whether line is long
				line = word.split('\n')[-1] + nextLine(text[iter + len(word):])
				if len(line) > rulesModule.rules.maxCharachterInLine:
					rulesModule.rules.lineIsLong = True
				else:
					rulesModule.rules.lineIsLong = False
				rulesModule.rules.hasLiteralOnLine = False
				rulesModule.rules.isLine = False
				# check whether line is comment
				rulesModule.rules.isComment = ifLineIsComment(text[iter + len(word):])

		elif isAlpha:
			if word in ["switch", "enum", "func"]:
				rulesModule.rules.lastKeyword = word
			if not isPrevSpace:
				result += checkWords(prevWord, "", word)
			result += word
		else:
			if word in "{([":
				rulesModule.rules.charStack.append(word)
				rulesModule.rules.indentLevel += 1
			elif word in "])}":
				rulesModule.rules.charStack = rulesModule.rules.charStack[:-1]
				rulesModule.rules.indentLevel -= 1
			elif "\"" in word and "\"\"" not in word and "\\\"" not in word:
				rulesModule.rules.isLine = not rulesModule.rules.isLine
				rulesModule.rules.hasLiteralOnLine = True
			if not isPrevSpace:
				result += checkWords(prevWord, "", word)
			result += word
		
		iter += len(word)

	output = open(outputFilename, mode="w")
	output.write(result)
	output.close()

parser = argparse.ArgumentParser(description='Swift formatter')
parser.add_argument("--filePath", help="Path to the file with swift code", required=True)
parser.add_argument("--configurationFileName", help="Name of the configuration file", required=True)
parser.add_argument("--outputFileName", help="Name of the file where output will be saved", required=True)
args = parser.parse_args()
importRules(args.configurationFileName)
formatFile(args.filePath, args.outputFileName)
exit()