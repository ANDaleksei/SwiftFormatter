from abc import *
import importlib

operators = ["=", "+=", "-=", "/=", "*=", "&&", "||", "==", "<", ">", "<=", ">=", "&", "|", "^", "+", "-", "*", "/", "%", "<<", ">>", "..<", "->"]
keywords = ["else", "while", "catch"]

class Rule(ABC):
	name = ""

	@abstractmethod
	def apply(self, prevWord, space, nextWord):
		pass

class BeforeParenthesses(Rule):
	name = "Rule name: before parenthesses"

	def apply(self, prevWord, space, nextWord):
		if nextWord == "(" and "\n" not in space:
			space = " " if rules.beforeParenthesses else ""
			return True, space
		else:
			return False, None

class AroundOperators(Rule):
	name = "Rule name: around operators"

	def apply(self, prevWord, space, nextWord):
		if "\n" in space:
			return False, None
		if (len(nextWord) != 0 and nextWord in operators) or (len(prevWord) != 0 and prevWord in operators):
			space = " " if rules.aroundOperators else ""
			return True, space
		else:
			return False, None

class BeforeLeftBrace(Rule):
	name = "Rule name: before left brace"

	def apply(self, prevWord, space, nextWord):
		if nextWord == "{" and "\n" not in space:
			space = " " if rules.beforeLeftBrace else ""
			return True, space
		else:
			return False, None

class BeforeKeyword(Rule):
	name = "Rule name: before keyword"

	def apply(self, prevWord, space, nextWord):
		if len(nextWord) != 0 and nextWord in keywords and "\n" not in space:
			space = " " if rules.beforeKeyword else ""
			return True, space
		else:
			return False, None

class Within(Rule):
	name = "Rule name: within"

	def apply(self, prevWord, space, nextWord):
		prevPredicate = (len(prevWord) != 0 and prevWord in "{([") and "\n" not in space
		nextPredicate = (len(nextWord) != 0 and nextWord in "])}") and "\n" not in space
		if prevPredicate or nextPredicate:
			space = " " if rules.within else ""
			return True, space
		else:
			return False, None

class BeforeColons(Rule):
	name = "Rule name: before colons"

	def apply(self, prevWord, space, nextWord):
		if nextWord == ":" and "\n" not in space:
			space = " " if rules.beforeColons else ""
			return True, space
		else:
			return False, None

class AfterColons(Rule):
	name = "Rule name: after colons"

	def apply(self, prevWord, space, nextWord):
		if prevWord == ":" and "\n" not in space:
			space = " " if rules.afterColons else ""
			return True, space
		else:
			return False, None

class WrappingOpenBrace(Rule):
	name = "Rule name: wrapping open brace"

	def apply(self, prevWord, space, nextWord):
		if nextWord == "{" and "\n" not in space:
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingOpenBrace else ""
			return True, space
		else:
			return False, None

class WrappingOpenParenthesses(Rule):
	name = "Rule name: wrapping open parenthesses"

	def apply(self, prevWord, space, nextWord):
		if prevWord == "(" and "\n" not in space:
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingOpenParenthesses else ""
			return True, space
		else:
			return False, None

class WrappingParameter(Rule):
	name = "Rule name: wrapping parameter"

	def apply(self, prevWord, space, nextWord):
		isParenthessesLast = len(rules.charStack) != 0 and rules.charStack[-1] == "("
		if prevWord == "," and "\n" not in space and isParenthessesLast:
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingParameter else ""
			return True, space
		else:
			return False, None

class WrappingCloseParenthesses(Rule):
	name = "Rule name: wrapping close parenthesses"

	def apply(self, prevWord, space, nextWord):
		wrapLine = rules.wrapLineIfLong and rules.lineIsLong
		if nextWord == ")" and "\n" not in space and (rules.wrappingCloseParenthesses or wrapLine):
			space = "\n" + rules.indentLevel * rules.spaces
			return True, space
		else:
			return False, None

class WrappingCloseBrace(Rule):
	name = "Rule name: wrapping close brace"

	def apply(self, prevWord, space, nextWord):
		wrapLine = rules.wrapLineIfLong and rules.lineIsLong
		if len(prevWord) != 0 and prevWord in "}" and "\n" not in space:
			space = "\n" + rules.indentLevel * rules.spaces if (rules.wrappingCloseBrace or wrapLine) else ""
			return True, space
		else:
			return False, None

class WrapLineIfLong(Rule):
	name = "Rule name: wrap line if long"

	def apply(self, prevWord, space, nextWord):
		comma = "," in prevWord and "\n" not in space
		openParenthesses = ("(" in prevWord) and ("\n" not in space)
		openBrace = prevWord == "{" and "\n" not in space
		if len(prevWord) != 0 and (comma or openParenthesses or openBrace) and rules.lineIsLong:
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrapLineIfLong else " "
			return True, space
		else:
			return False, None

class DefaultSpaceFormatter(Rule):
	name = "Rule name: default space formatter"

	def apply(self, prevWord, space, nextWord):
		count = space.count("\n")
		if count == 0:
			return True, (" " if len(space) > 0 else "")
		else:
			res = ""
			if count > 1:
				emptyLineIndent = ""
				if rules.isMultilineComment and not rules.indentMultilineString:
					emptyLineIndent = ""
				if rules.keepIndentOnEmptyLines:
					emptyLineIndent = rules.indentLevel * rules.spaces
				else:
					emptyLineIndent = ""
				res = min((count - 1), rules.maxNumberOfEmptyLines) * ("\n" + emptyLineIndent)
			# last new line
			if rules.isMultilineComment and not rules.indentMultilineString:
				res += "\n"
			else:
				#print("Level", rules.indentLevel)
				res += "\n" + rules.indentLevel * rules.spaces
			# check next chat
			if nextWord in "})]":
				res = res[0:-(len(rules.spaces))]
			elif nextWord in ".":
				res += rules.spaces
			return True, res

class SkipFormatting(DefaultSpaceFormatter):
	name = "Rule name: skip formatting if it comment"

	def apply(self, prevWord, space, nextWord):
		if rules.isComment:
			return super().apply(prevWord, space, nextWord)
		else:
			return False, None

rules = None
allRules = None
def importConfiguration(configurationFilename):
	module = __import__(configurationFilename)
	global rules
	rules = module.FormattingRules()
	# additional
	rules.indentLevel = 0
	rules.spaces = (indent * "\t") if rules.useTab else (rules.indent * " ")
	rules.isMultilineComment = False
	rules.isComment = False
	rules.lineIsLong = False
	rules.charStack = list()
	global allRules
	allRules = [
		SkipFormatting(),
		WrapLineIfLong(),
		BeforeParenthesses(),
		BeforeLeftBrace(),
		BeforeKeyword(),
		BeforeColons(),
		AfterColons(),
		WrappingOpenBrace(),
		WrappingOpenParenthesses(),
		WrappingParameter(),
		WrappingCloseParenthesses(),
		WrappingCloseBrace(),
		AroundOperators(),
		Within(),
		DefaultSpaceFormatter()
	]









