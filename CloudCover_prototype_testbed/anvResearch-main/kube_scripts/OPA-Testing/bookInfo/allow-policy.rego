package envoy.authz

import future.keywords

default allow = false

allow if {
	path_allowed
	token_match
}

path_allowed if {
		allowed_sources := [
			"productpage,reviews,ratings",
			"productpage,reviews",
			"productpage,details",
			"productpage",
		] # Append all valid paths into this array

	encoded := input.attributes.request.http.headers
	encoded.sources in allowed_sources
}

token_match if {
	tokenMap := [
		{"sName": "productpage", "tokVal": "pp"},
		{"sName": "details", "tokVal": "det"},
		{"sName": "reviews", "tokVal": "rev"},
		{"sName": "ratings", "tokVal": "rat"},
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
