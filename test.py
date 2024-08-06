def clean_json_text(res_txt):

    start_idx = res_txt.find('{')
    end_idx = res_txt.rfind('}') + 1

    # Extract the JSON substring
    if start_idx != -1 and end_idx != -1:
        res_txt = res_txt[start_idx:end_idx]

    return res_txt

# Example usage
res_txt = """

    {
        "key": "value",
        "array": [1, 2, 3],
        "object": {"nested_key": "nested_value"}
    }

```"""
cleaned_json = clean_json_text(res_txt)
print(cleaned_json)
