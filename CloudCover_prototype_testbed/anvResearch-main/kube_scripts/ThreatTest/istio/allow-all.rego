package envoy.authz

import future.keywords

default allow = false

allow if {
	path_allowed
	token_match
}

path_allowed if {
		allowed_sources := [
			"ext,frontend,checkout",
			"ext,frontend",
			"ext,logs",
			"ext,logs",
            		"ext",
		] # Append all valid paths into this array

	encoded := input.attributes.request.http.headers
	encoded.sources in allowed_sources
}

token_match if {
	tokenMap := [
    	{"sName": "ext", "tokVal": "ext"},
		{"sName": "frontend", "tokVal": "frontend"},
		{"sName": "checkout", "tokVal": "checkout"},
		{"sName": "payment", "tokVal": "payment"},
		{"sName": "logs", "tokVal": "logs"},
	] # Append all serviceName + token pairs into this array

	encoded := input.attributes.request.http.headers
	sourcesList := split(encoded.sources, ",")
	tokensList := split(encoded.tokens, ",")
	every source in sourcesList {
		some i
		source == sourcesList[j]
		tokenMap[i].sName == source
		tokenMap[i].tokVal == tokensList[j]
	}

	every token in tokensList {
		some i
		token == tokensList[j]
		tokenMap[i].tokVal == token
		tokenMap[i].sName == sourcesList[j]
	}
}
