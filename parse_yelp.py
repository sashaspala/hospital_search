import json
import os

class Parser:
	def __init__(self, dataset_path):
		self.path = dataset_path
		self.hosp_ids = []


	def find_hospitals(self):
		data = []
		with open(os.path.join(self.path, 'yelp_academic_dataset_business.json')) as data_file:
			for line in data_file:
				data.append(json.loads(line))

		hosp_json = []
		hospital_attributes = ["Medical Centers", "Hospitals","Health & Medical"]
		for business in data:
			#make sure this business matches some hospital queries
			found = False
			for category in hospital_attributes:
				if business['categories'] is not None and category in business['categories'] and not found:
					# got a potential hospital! add to our smaller json file
					id = business['business_id']
					hosp_json.append(business)
					self.hosp_ids.append(id) # so we can easily match these later if we need to
					found = True
		return hosp_json

	def save_to_file(self, data_dict):
		with open('expanded_dataset.json', 'w') as outfile:
			json.dump(data_dict, outfile)

	def get_reviews(self):
		with open('expanded_reviews_all.json', 'w') as outfile:
			json_list = []
			counter = 0
			with open('yelp_dataset_challenge_round9/yelp_academic_dataset_review.json', 'r') as data_file:
				for line in data_file:
					json_line = json.loads(line)
					if json_line['business_id'] in self.hosp_ids:
						counter += 1
						if counter % 500 == 0:
							print(counter)
						#add this dictionary to the list
						json_list.append(json_line)
						if counter == 30000:
							break
			json.dump(json_list, outfile)


if __name__ == "__main__":
	parser = Parser('yelp_dataset_challenge_round9')
	json_dict = parser.find_hospitals()
	parser.save_to_file(json_dict)
	parser.get_reviews()