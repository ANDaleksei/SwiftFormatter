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
		if nextWord == "(":
			space = " " if rules.beforeParenthesses else ""
			return True, space
		else:
			return False, None

class AroundOperators(Rule):
	name = "Rule name: around operators"

	def apply(self, prevWord, space, nextWord):
		if (len(nextWord) != 0 and nextWord in operators) or (len(prevWord) != 0 and prevWord in operators):
			space = " " if rules.aroundOperators else ""
			return True, space
		else:
			return False, None

class BeforeLeftBrace(Rule):
	name = "Rule name: before left brace"

	def apply(self, prevWord, space, nextWord):
		if nextWord == "{":
			space = " " if rules.beforeLeftBrace else ""
			return True, space
		else:
			return False, None

class BeforeKeyword(Rule):
	name = "Rule name: before keyword"

	def apply(self, prevWord, space, nextWord):
		if len(nextWord) != 0 and nextWord in keywords:
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
		if nextWord == ":":
			space = " " if rules.beforeColons else ""
			return True, space
		else:
			return False, None

class AfterColons(Rule):
	name = "Rule name: after colons"

	def apply(self, prevWord, space, nextWord):
		if len(prevWord) != 0 and prevWord in ":":
			space = " " if rules.afterColons else ""
			return True, space
		else:
			return False, None

class WrappingOpenBrace(Rule):
	name = "Rule name: wrapping open brace"

	def apply(self, prevWord, space, nextWord):
		if nextWord == "{":
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingOpenBrace else ""
			return True, space
		else:
			return False, None

class WrappingOpenParenthesses(Rule):
	name = "Rule name: wrapping open parenthesses"

	def apply(self, prevWord, space, nextWord):
		if len(prevWord) != 0 and prevWord in "(":
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingOpenParenthesses else ""
			return True, space
		else:
			return False, None

class WrappingParameter(Rule):
	name = "Rule name: wrapping parameter"

	def apply(self, prevWord, space, nextWord):
		if len(prevWord) != 0 and prevWord in ",":
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingParameter else ""
			return True, space
		else:
			return False, None

class WrappingCloseParenthesses(Rule):
	name = "Rule name: wrapping close parenthesses"

	def apply(self, prevWord, space, nextWord):
		if len(prevWord) != 0 and prevWord in "(":
			space = "\n" + rules.indentLevel * rules.spaces if rules.wrappingCloseParenthesses else ""
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
				res = (count - 1) * ("\n" + emptyLineIndent)
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

rules = None
allRules = None
def importConfiguration(configurationFilename):
	module = __import__(configurationFilename)
	global rules
	rules = module.FormattingRules()
	global allRules
	allRules = [
		BeforeParenthesses(),
		AroundOperators(),
		BeforeLeftBrace(),
		BeforeKeyword(),
		Within(),
		BeforeColons(),
		AfterColons(),
		WrappingOpenBrace(),
		WrappingOpenParenthesses(),
		WrappingParameter(),
		WrappingCloseParenthesses(),
		DefaultSpaceFormatter()
	]









