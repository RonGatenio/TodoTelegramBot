def clean_string(string, *substrings_to_remove):
    for s in substrings_to_remove:
        if s:
            string = string.replace(s, '')
    return string.strip()
