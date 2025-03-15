def html_decode(encoded_str):

    import re

    def replace_entity(match):
        code = match.group(1)
        return chr(int(code))

    
    return re.sub(r'&#(\d+);', replace_entity, encoded_str)

def url_decode(encoded_str):
    
    result = b""   
    i = 0
    while i < len(encoded_str):
        char = encoded_str[i]
        if char == "%":
            
            hex_value = encoded_str[i + 1:i + 3]
            try:
                result += bytes([int(hex_value, 16)])
                i += 3
            except ValueError:
                result += b"%" 
                i += 1
        elif char == "+":
            
            result += b" "
            i += 1
        else:
            result += char.encode('latin1')
            i += 1

    
    return html_decode(result.decode("utf-8"))
