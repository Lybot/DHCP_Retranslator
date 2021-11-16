class ParsePacket:
	def __init__(self, str_packet):
		self.str_packet = str_packet
		self.src_ip = str_packet[26:30]
		self.dst_ip = str_packet[30:34]
		self.src_mac = str_packet[0:6]
		self.dst_mac = str_packet[6:12]

	def change_mac(self, src_mac, dst_mac):
		self.str_packet = self.str_packet.replace(self.str_packet[0:12], bytes.fromhex(dst_mac.replace(":", "")) + bytes.fromhex(src_mac.replace(":", "")))

	def change_ip(self, src_ip, dst_ip):
		def str_to_hex_ip(ip):
			ip_numbers = ip.split('.')
			result = []
			for number in ip_numbers:
				result.append(int(number))
			byte_result = bytes(result)
			return byte_result
		self.str_packet= self.str_packet.replace(self.str_packet[26:34], str_to_hex_ip(src_ip)+ str_to_hex_ip(dst_ip))

	def get_src_ip(self):
		src_ip = ""
		for number in self.src_ip:
			src_ip += str(number) + "."
			# src_ip += str(int(number.encode('hex'), 16)) + "."
		src_ip = src_ip[0:(len(src_ip)-1)]
		return src_ip

	def get_dst_ip(self):
		dst_ip = ""
		for number in self.dst_ip:
			dst_ip += str(int(number.encode('hex'), 16)) + "."
		dst_ip = dst_ip[0:(len(dst_ip)-1)]
		return dst_ip

	def __str__(self):
		result = self.str_packet
		return result

	def __len__(self):
		return len(self.str_packet)
