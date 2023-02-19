FORMAT = "utf-8"

def serialize(data):
  data_string = data["version"].encode(FORMAT)
  data_string += data["operation"].encode(FORMAT)
  data_string += data["info"].encode(FORMAT)
  return data_string

def deserialize(data):
  data = data.decode()
  decoded_data = {}
  decoded_data["version"] = data[0]
  decoded_data["operation"] = data[1:3]
  decoded_data["info"] = data[3:]

  return decoded_data

# Client to server: " LENGTH " then " VERSION OPERATION MESSAGE "
# Server to client: " LENGTH " then " VERSION OPERATION MESSAGE "