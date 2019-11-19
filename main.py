from rules import *
import sys
import argparse

rulesModule = None

def importRules(configurationFilename):
	global rulesModule
	rulesModule = __import__("rules")
	print(rulesModule)
	rulesModule.importConfiguration(configurationFilename)
	print("I'm here")
	print(rulesModule.allRules)

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
		if ((char in " \t\n") == isSpace) and ((char.isalpha() or (char in "#")) == isAlpha) and (char not in "{([])}"):
			word += char
		else:
			return word
	return word

def checkWords(prevWord, spaces, nextWord):
	for rule in rulesModule.allRules:
		isApplied, space = rule.apply(prevWord, spaces, nextWord)
		if isApplied:
			print(rule.name, prevWord, "spaces", nextWord)
			return space
	# if no rule was applied, actually should not be called
	return spaces

def formatFile(filename, outputFilename):
	file = open(filename)
	text = file.read()
	file.close()

	allSpaces = " \n\t"
	charStack = ""
	spaces = ""
	word = ""
	result = ""
	lineCharStack = ""
	indentDecreased = False
	# multiline
	quteCount = 0
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
		elif isAlpha:
			if not isPrevSpace:
				result += checkWords(prevWord, "", word)
			result += word
		else:
			if word in "{([":
				rulesModule.rules.indentLevel += 1
			elif word in "])}":
				rulesModule.rules.indentLevel -= 1
			if not isPrevSpace:
				result += checkWords(prevWord, "", word)
			result += word
		# spaces
		# if isSpace:
		# 	if "\n" in word:
		# 		if len(lineCharStack) > 0:
		# 			rules.indentLevel += 1
		# 		lineCharStack = ""
		# 		indentDecreased = False
		# 	result += formatSpaces(word, nextWord(text[iter-1::-1], False)[::-1], nextWord(text[iter:], False))
		# 	if nextChar in "." and "\n" in word:
		# 		charStack += nextChar
		# 		rules.indentLevel += 1
		# elif isAlpha:
		# 	if not isPrevSpace:
		# 		result += formatSpaces("", nextWord(text[iter-1::-1], False)[::-1], nextWord(text[iter:], False))	
		# 	result += word
		# else:
		# 	if "\n" not in prevWord:
		# 		result += formatSpaces("", nextWord(text[iter-1::-1], False)[::-1], nextWord(text[iter:], False))
		# 	result += word
		# 	if word == "\"\"\"":
		# 		rules.isMultilineComment = not rules.isMultilineComment
		# 	# indents
		# 	if word in "{([":
		# 		charStack += word
		# 		lineCharStack += word
		# 	elif word in "})]":
		# 		charStack = charStack[:-1]
		# 		if len(lineCharStack) != 0:
		# 			lineCharStack = lineCharStack[:-1]
		# 		elif not indentDecreased:
		# 			rules.indentLevel -= 1
		# 			indentDecreased = True
		# 		if len(charStack) > 0 and charStack[-1] == '.':
		# 			charStack = charStack[:-1]
		# 			rules.indentLevel -= 1
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