class FormattingRules:
	# rules
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
	wrappingCloseParenthesses = False
	# additional
	indentLevel = 0
	spaces = (indent * "\t") if useTab else (indent * " ")

	isMultilineComment = False