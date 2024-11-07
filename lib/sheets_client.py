
import gspread

from google.oauth2.service_account import Credentials


class SheetsClient():

	CREDENTIALS_FILENAME = "retrolection-creds.json"

	SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

	def __init__(self, sheet_id):
		creds = Credentials.from_service_account_file(SheetsClient.CREDENTIALS_FILENAME, scopes=SheetsClient.SCOPES)
		self.client = gspread.authorize(creds)

		self.spreadsheet = self.client.open_by_key(sheet_id)

		
	def get_values(self, ranges):
		return self.spreadsheet.values_batch_get(ranges)

	def set_values(self, ranges_values):
		self.spreadsheet.values_batch_update({"valueInputOption": "USER_ENTERED", "data": ranges_values})
		
	def get_sheets(self):
		return self.spreadsheet.worksheets()
