class FormattingRules:
	# rules
	maxCharachterInLine = 80
	useTab = False
	indent = 2
	keepIndentOnEmptyLines = False
	indentMultilineString = True
	beforeParenthesses = False
	aroundOperators = True
	beforeLeftBrace = True
	beforeKeyword = True
	within = True
	beforeColons = False
	afterColons = True
	wrappingOpenBrace = False
	wrappingOpenParenthesses = False
	wrappingParameter = False
	wrappingCloseBrace = True
	wrappingCloseParenthesses = False
	wrapLineIfLong = True
	maxNumberOfEmptyLines = 1
	# additional
	indentLevel = 0
	spaces = (indent * "\t") if useTab else (indent * " ")
	isMultilineComment = False
	lineIsLong = False