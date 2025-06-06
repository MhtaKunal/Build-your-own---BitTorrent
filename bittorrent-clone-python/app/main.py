import json
import sys
import bencodepy


# import bencodepy - available if you need it!
# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"
def decode_bencode(bencoded_value):
    # This is the inbuilt decoder function from bencodepy library
    return bencodepy.Bencode(encoding='utf-8').decode(bencoded_value)


    # Self defined function, we can use either one
    def decode_each(index):
        if chr(bencoded_value[index]).isdigit():
            first_colon_index = bencoded_value.find(b":", index)
            if first_colon_index == -1:
                raise ValueError("Invalid encoded value")
            length = int(bencoded_value[index:first_colon_index])
            return str(bencoded_value[first_colon_index + 1:first_colon_index + 1 + length],
                       'utf-8'), first_colon_index + 1 + length
        elif chr(bencoded_value[index]) == 'i':
            end_index = bencoded_value.find(b"e", index)
            return int(bencoded_value[index + 1: end_index]), end_index + 1
        elif bencoded_value[index] == ord("l"):  # List
            index += 1  # Move past 'l'
            result = []
            while bencoded_value[index] != ord("e"):  # Loop until 'e'
                item, index = decode_each(index)  # Recursive decode
                result.append(item)
            return result, index + 1  # Skip 'e'
        elif bencoded_value[index] == ord("d"):
            result = {}
            index += 1  # Move past 'd'
            key, current_key = 1, ""
            while bencoded_value[index] != ord("e"):  # Loop until 'e'
                key, index = decode_each(index)
                value, index = decode_each(index)
                result[key] = value
                # item, index = decode_each(index)
                # if key:
                #     result[item] = ""
                #     current_key = item
                #     key = 0 # This flag switch makes sure, value is assigned after the key
                # else:
                #     result[current_key] = item
                #     key = 1     # this flag switch ensures addition of new key

            return result, index + 1
        else:
            raise NotImplementedError("Only strings and integers are supported at the moment")

    decoded_value, last_index = decode_each(0)
    return decoded_value


def extract_torrent_info(torrent_file_path):
    with open(torrent_file_path, "rb") as f:
        bencoded_data = f.read()  # Read raw Bencoded content

    decoded_data = decode_bencode(bencoded_data)  # Decode Bencode data

    tracker_url = decoded_data.get("announce", b"Unknown tracker").decode(
        "utf-8"
    )  # Fix: Convert bytes to string
    file_length = decoded_data.get("info", {}).get("length", "Unknown length")

    print(f"Tracker URL: {tracker_url}")
    print(f"Length: {file_length}")


def main():
    command = "decode"

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = b"d5:helloi52e3:foo3:bare"

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    elif command == "info":
        torrent_file_path = sys.argv[2]
        extract_torrent_info(torrent_file_path)  # Call extraction function
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
