
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class SheetsClient():

	CREDENTIALS_FILENAME = "credentials.json"
	TOKEN_FILENAME = "token.json"
	# If modifying these scopes, delete the file token.json.
	SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

	def __init__(self, sheet_id):
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists(SheetsClient.TOKEN_FILENAME):
			creds = Credentials.from_authorized_user_file(SheetsClient.TOKEN_FILENAME, SheetsClient.SCOPES)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(SheetsClient.CREDENTIALS_FILENAME, SheetsClient.SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(SheetsClient.TOKEN_FILENAME, "w") as token:
				token.write(creds.to_json())

		service = build("sheets", "v4", credentials=creds)

		# Call the Sheets API
		self.sheet_service = service.spreadsheets()
		self.sheet_id = sheet_id
		
	def get_values(self, ranges):
		request = self.sheet_service.get(
			spreadsheetId=self.sheet_id,
			ranges=ranges,
			fields="properties.title,sheets(properties,data.startColumn,data.startRow,data.rowData.values(formattedValue,userEnteredFormat))")
		
		return request.execute()
		
	def set_values(self, ranges_values):
		request = self.sheet_service.values().batchUpdate(
			spreadsheetId=self.sheet_id,
			body={"valueInputOption": "USER_ENTERED", "data": ranges_values}
		)
		
		request.execute()
		
	def get_sheets(self):
		request = self.sheet_service.get(
			spreadsheetId=self.sheet_id)
		
		return request.execute()
		