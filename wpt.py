from xml.dom import minidom

class WptResultData(object):

	def __init__(self, result):

		xml = minidom.parseString(result)

		



