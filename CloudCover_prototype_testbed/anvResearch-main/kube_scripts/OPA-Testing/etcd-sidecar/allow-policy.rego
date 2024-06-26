package envoy.authz

import future.keywords

default allow = false

allow if {
	path_allowed
	token_match
}

path_allowed if {
		allowed_sources := [
			"ext,fs1,fs2,fs3,fs4,fs5",
			"ext,fs1,fs2,fs3,fs4",
			"ext,fs1,fs2,fs3",
			"ext,fs1,fs2",
			"ext,fs1",
            		"ext",
		] # Append all valid paths into this array

	encoded := input.attributes.request.http.headers
	encoded.sources in allowed_sources
}

token_match if {
	tokenMap := [
    	{"sName": "ext", "tokVal": "ext"},
		{"sName": "fs1", "tokVal": "token1"},
		{"sName": "fs2", "tokVal": "token2"},
		{"sName": "fs3", "tokVal": "token3"},
		{"sName": "fs4", "tokVal": "token4"},
		{"sName": "fs5", "tokVal": "token5"},
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
