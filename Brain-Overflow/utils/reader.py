import struct 
import os
import datetime as dt

USER_ID_BYTES_SIZE = 8
USER_INFO_FIXED_SIZE = 17
SNAPSHOT_FORMAT = 'ldddddddII'

class Reader:
	def __init__(self, path):
		self.path = path
		self.offset = 0
		with open(self.path, "rb") as file:
			self.extract_user_info(file)
	
	def __iter__(self):
		with open(self.path, "rb") as file:
			for i in self.process_snapshots(file):
				yield i

	def read_var_in_requested_format(self, file, bin_length, requested_format, decode=False):
		var_bin_rep = file.read(bin_length)
		var_requested_rep = struct.unpack(requested_format, var_bin_rep)
		if len(var_requested_rep) < 2:
			var_requested_rep = var_requested_rep[0]
		if decode:
			var_requested_rep = var_requested_rep.decode()
		return var_requested_rep

	def extract_user_info(self, file):
		self.user_id = self.read_var_in_requested_format(file, USER_ID_BYTES_SIZE, 'l')
		user_name_size = self.read_var_in_requested_format(file, 4, 'i')
		self.user_name = self.read_var_in_requested_format(file, user_name_size, '{0}s'.format(user_name_size), True)
		self.user_birth_date = self.read_var_in_requested_format(file, 4, 'i')
		self.user_gender = self.read_var_in_requested_format(file, 1, 'c', True)
		self.offset = USER_INFO_FIXED_SIZE + user_name_size

	def gen_next_snapshot_ts(self, file):
		file.seek(self.offset)
		try:
			data = self.read_var_in_requested_format(file, 8, 'Q')
			while data:
				yield data
				data = self.read_var_in_requested_format(file, 8, 'Q')
		finally:
			return

	def process_snapshots(self, file):
		ts_gen = self.gen_next_snapshot_ts(file)
		for ts in ts_gen:
			datetime = dt.datetime.fromtimestamp(ts/1000.0)
			translation = self.read_var_in_requested_format(file, 24, 'ddd')
			rotation = self.read_var_in_requested_format(file, 32, 'dddd')
			color_image_dimension = self.read_var_in_requested_format(file,8, 'II')
			color_image_size = color_image_dimension[0] * color_image_dimension[1]
			color_image_vals = file.read(color_image_size*3)
			depth_image_dimension = self.read_var_in_requested_format(file,8, 'II')
			depth_image_size = depth_image_dimension[0] * depth_image_dimension[1]
			depth_image_vals = file.read(depth_image_size*4)
			user_feelings = self.read_var_in_requested_format(file, 4*4, 'ffff')
			#TODO - Create snapshot object?
			yield datetime

x = Reader('sample.mind')
for s in x:
	print(s)

