#from enum import Enum

# stopped using enum because it meant client / server couldn't identify it was same value

class Operations:
  # SERVER SIDE OPERATIONS (sent to client)
  SUCCESS = "00"
  FAILURE = "01"
  ACCOUNT_ALREADY_EXISTS = "02"
  ACCOUNT_DOES_NOT_EXIST = "03"
  LIST_OF_ACCOUNTS = "04"
  LIST_OF_MESSAGES = "05"

  # CLIENT SIDE OPERATIONS (sent to server)
  LOGIN = "10"
  CREATE_ACCOUNT = "11"
  DELETE_ACCOUNT = "12"
  LIST_ACCOUNTS = "13"
  SEND_MESSAGE = "14"
  VIEW_UNDELIVERED_MESSAGES = "15"