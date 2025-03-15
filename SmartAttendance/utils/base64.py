BASE64_ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def base64_encode(data):

    if isinstance(data, str): 
        data = data.encode('utf-8')

    encoded = bytearray()
    padding = (3 - len(data) % 3) % 3 
    data += b'\x00' * padding  

    for i in range(0, len(data), 3):
        triple = (data[i] << 16) + (data[i + 1] << 8) + data[i + 2]
        encoded.append(BASE64_ALPHABET[(triple >> 18) & 0x3F])
        encoded.append(BASE64_ALPHABET[(triple >> 12) & 0x3F])
        encoded.append(BASE64_ALPHABET[(triple >> 6) & 0x3F])
        encoded.append(BASE64_ALPHABET[triple & 0x3F])

   
    if padding > 0:
        encoded[-padding:] = b'=' * padding

    return encoded.decode('ascii')


def base64_decode(encoded_data):

    
    encoded_data = encoded_data.rstrip('=')

    
    decoded = bytearray()

    
    for i in range(0, len(encoded_data), 4):
        quadruple = 0
        padding = 4 - len(encoded_data[i:i+4])
        for j, char in enumerate(encoded_data[i:i+4]):
            quadruple |= BASE64_ALPHABET.index(char.encode('ascii')) << (18 - 6 * j)

        decoded.append((quadruple >> 16) & 0xFF)
        if padding < 2:
            decoded.append((quadruple >> 8) & 0xFF)
        if padding < 1:
            decoded.append(quadruple & 0xFF)

    return bytes(decoded)


